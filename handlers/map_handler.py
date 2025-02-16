import logging
import json
import math
from datetime import datetime
import gpxpy
import gpxpy.gpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Location
from telegram.ext import ContextTypes
from core.states import States
from database.db_manager import DatabaseManager
from services.map_service import MapService
from config.api_config import MAP_UPDATE_INTERVAL
from services.gps_handler import GPSHandler
from services.map_cache_service import MapCacheService
from services.track_compression import TrackCompressor
from services.track_export import TrackExporter
from services.track_analyzer import TrackAnalyzer
from core.map_manager import MapManager
from services.yandex_maps_service import YandexMapsService
from utils.location_permission_manager import LocationPermissionManager

logger = logging.getLogger(__name__)

class MapHandler(BaseHandler):
    def __init__(self, db_manager: DatabaseManager):
        super().__init__(db_manager)
        self.gps_handler = GPSHandler()
        self.map_cache = MapCacheService()
        self.track_compressor = TrackCompressor()
        self.track_exporter = TrackExporter()
        self.active_tracks = {}  # user_id: {track_id, points}
        self.map_service = MapService()
        self.location_updates = {}  # user_id: last_update_time
        self.live_tracking_users = set()  # Для отслеживания пользователей с включенным live-трекингом
        self.location_permission_manager = LocationPermissionManager(db_manager)

    async def show_map_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Показ меню карты"""
        keyboard = [
            [InlineKeyboardButton("📍 Начать запись трека", callback_data="start_track")],
            [InlineKeyboardButton("⏹ Завершить запись трека", callback_data="stop_track")],
            [InlineKeyboardButton("📊 Мои треки", callback_data="my_tracks")],
            [InlineKeyboardButton("📍 Отправить местоположение", callback_data="send_location")],
            [InlineKeyboardButton("🗺 Карта онлайн", callback_data="online_map")],
            [InlineKeyboardButton("« Назад", callback_data="back_to_main")]
        ]
        
        await update.callback_query.message.edit_text(
            "🗺 Меню карты\n\n"
            "• Записывайте треки своих маршрутов\n"
            "• Отправляйте свое местоположение\n"
            "• Следите за участниками поиска онлайн",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return True

    async def handle_map_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Центральный обработчик callback'ов карты"""
        query = update.callback_query
        data = query.data
        user_id = update.effective_user.id
        
        try:
            if data == "map_main":
                await self.show_map_menu(update, context)
            
            elif data == "start_track":
                if user_id in self.active_tracks:
                    await query.answer("У вас уже есть активный трек!")
                    return
                await self.handle_track_start(update, context)
            
            elif data == "stop_track":
                if user_id not in self.active_tracks:
                    await query.answer("У вас нет активного трека!")
                    return
                await self.handle_track_stop(update, context)
            
            elif data == "my_tracks":
                await self.show_tracks_list(update, context)
            
            elif data == "send_location":
                await self.request_location(update, context)
            
            elif data == "online_map":
                await self.show_online_map(update, context)
            
            else:
                logger.warning(f"Неизвестный callback для карты: {data}")
                await query.answer("Функция недоступна")
                
        except Exception as e:
            logger.error(f"Ошибка в обработчике карты: {e}")
            await query.answer("Произошла ошибка")
            await self.show_map_menu(update, context)

    async def handle_track_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало записи трека"""
        query = update.callback_query
        user_id = update.effective_user.id
        
        if user_id in self.active_tracks:
            await query.answer("У вас уже есть активный трек!")
            return
        
        # Создаем новый трек
        track_id = await self.db.create_track(user_id)
        self.active_tracks[user_id] = {
            'track_id': track_id,
            'points': []
        }
        
        keyboard = [
            [InlineKeyboardButton("⏹ Завершить запись", callback_data="stop_track")],
            [InlineKeyboardButton("« Назад", callback_data="map_menu")]
        ]
        
        await query.message.edit_text(
            "📍 Запись трека начата!\n\n"
            "• Отправляйте свое местоположение\n"
            "• Все точки будут автоматически записаны\n"
            "• По завершении нажмите 'Завершить запись'",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        await query.answer("Запись трека начата!")

    async def handle_track_stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Завершение записи трека"""
        user_id = update.effective_user.id
        track_data = self.active_tracks.pop(user_id)
        
        # Сохраняем трек в базу
        track_info = {
            'id': track_data['track_id'],
            'user_id': user_id,
            'points': track_data['points'],
            'start_time': track_data['start_time'],
            'end_time': datetime.now()
        }
        
        await self.db.save_track(track_info)
        
        # Генерируем статистику трека
        stats = self.track_analyzer.analyze_track(track_data['points'])
        
        keyboard = [
            [InlineKeyboardButton("📊 Показать трек", callback_data=f"show_track_{track_data['track_id']}")],
            [InlineKeyboardButton("« В меню карты", callback_data="map_main")]
        ]
        
        await update.callback_query.message.edit_text(
            "✅ Запись трека завершена\n\n"
            f"📏 Пройдено: {stats['distance']:.2f} км\n"
            f"⏱ Время в пути: {stats['duration']}\n"
            f"📈 Средняя скорость: {stats['avg_speed']:.1f} км/ч",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def handle_location(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Обработка полученных координат"""
        user_id = update.effective_user.id
        location = update.message.location
        
        if user_id in self.active_tracks:
            # Добавляем точку к активному треку
            self.active_tracks[user_id]['points'].append({
                'lat': location.latitude,
                'lon': location.longitude,
                'time': update.message.date
            })
            
            await update.message.reply_text("📍 Точка добавлена к треку")
            return True
        
        if user_id in self.live_tracking_users:
            # Обновляем положение на карте
            await self.db.update_user_location(user_id, location.latitude, location.longitude)
            await update.message.reply_text("📍 Ваше положение обновлено")
            return True
        
        return False

    async def start_tracking(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало отслеживания позиции"""
        try:
            query = update.callback_query
            user_id = query.from_user.id
            
            # Получаем текущую группу пользователя
            group_id = await self.map_manager.db.get_user_active_group(user_id)
            if not group_id:
                await query.answer("❌ Вы не состоите в активной группе")
                return
                
            success = await self.map_manager.start_tracking(user_id, group_id)
            if success:
                await query.edit_message_text(
                    "✅ Отслеживание начато\n"
                    "Отправьте свою геопозицию для обновления местоположения",
                    reply_markup=self._get_tracking_keyboard()
                )
            else:
                await query.edit_message_text("❌ Не удалось начать отслеживание")
                
        except Exception as e:
            logger.error(f"Error starting tracking: {e}")
            await update.callback_query.answer("❌ Произошла ошибка")
            
    def _get_tracking_keyboard(self) -> InlineKeyboardMarkup:
        """Клавиатура для управления отслеживанием"""
        keyboard = [
            [
                InlineKeyboardButton("📍 Отправить позицию", callback_data="send_location"),
                InlineKeyboardButton("⏹ Остановить", callback_data="stop_tracking")
            ],
            [
                InlineKeyboardButton("🗺 Показать карту группы", callback_data="show_group_map"),
                InlineKeyboardButton("« Назад", callback_data="map_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    def calculate_distance(self, points):
        """Вычисление расстояния между точками по формуле гаверсинусов"""
        total_distance = 0
        for i in range(len(points) - 1):
            lat1, lon1 = points[i]['lat'], points[i]['lon']
            lat2, lon2 = points[i + 1]['lat'], points[i + 1]['lon']
            
            R = 6371  # радиус Земли в километрах
            
            # Перевод в радианы
            lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
            
            # Разница координат
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            # Формула гаверсинусов
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.asin(math.sqrt(a))
            distance = R * c
            
            total_distance += distance
        
        return total_distance

    def create_gpx(self, points, track_name="Track"):
        """Создание GPX файла из точек трека"""
        gpx = gpxpy.gpx.GPX()
        gpx_track = gpxpy.gpx.GPXTrack()
        gpx.tracks.append(gpx_track)
        
        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)
        
        for point in points:
            gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(
                point['lat'],
                point['lon'],
                time=datetime.fromisoformat(point['timestamp'])
            ))
        
        return gpx.to_xml()

    async def handle_track_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отображение списка сохраненных треков"""
        user_id = update.effective_user.id
        tracks = self.db.get_user_tracks(user_id)
        
        if not tracks:
            await update.callback_query.message.edit_text(
                "У вас пока нет сохраненных треков.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« Назад", callback_data="map_menu")
                ]])
            )
            return
        
        keyboard = []
        for track in tracks:
            track_date = datetime.fromisoformat(track['start_time']).strftime("%d.%m.%Y %H:%M")
            keyboard.append([
                InlineKeyboardButton(
                    f"📍 {track_date} ({track['distance']:.1f} км)",
                    callback_data=f"track_view_{track['track_id']}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("« Назад", callback_data="map_menu")])
        
        await update.callback_query.message.edit_text(
            "📊 Ваши треки:\n"
            "Выберите трек для просмотра:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def handle_track_view(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Просмотр информации о треке и визуализация на карте"""
        track_id = int(update.callback_query.data.split('_')[-1])
        track = self.db.get_track(track_id)
        
        if not track:
            await update.callback_query.message.edit_text(
                "❌ Трек не найден.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« Назад", callback_data="track_list")
                ]])
            )
            return
        
        points = json.loads(track['points_json'])
        
        # Генерируем карту с треком
        map_file = self.map_service.generate_dynamic_map([], track_points=points)
        
        if map_file:
            # Отправляем информацию о треке
            track_info = (
                f"📍 Трек #{track_id}\n\n"
                f"📅 Дата: {datetime.fromisoformat(track['start_time']).strftime('%d.%m.%Y %H:%M')}\n"
                f"📏 Расстояние: {track['distance']:.1f} км\n"
                f"📍 Точек: {len(points)}"
            )
            
            await update.callback_query.message.edit_text(track_info)
            
            # Отправляем карту и GPX файл
            with open(f"temp/{map_file}", "rb") as f:
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=f,
                    filename="track_map.html",
                    caption="🗺 Визуализация трека"
                )
            
            gpx_data = self.create_gpx(points, f"Track_{track_id}")
            with open(f"track_{track_id}.gpx", "w") as f:
                f.write(gpx_data)
            
            with open(f"track_{track_id}.gpx", "rb") as f:
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=f,
                    filename=f"track_{track_id}.gpx",
                    caption="📎 GPX файл трека"
                )
        else:
            await update.callback_query.message.edit_text(
                "❌ Не удалось сгенерировать карту. Попробуйте позже.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« Назад", callback_data="track_list")
                ]])
            )

    async def show_online_map(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Показ онлайн-карты с участниками"""
        user_id = update.effective_user.id
        active_search = await self.db.get_active_search(user_id)
        
        if not active_search:
            await update.callback_query.answer(
                "❌ Вы не участвуете в активном поиске",
                show_alert=True
            )
            return False

        # Получаем координаты всех участников
        participants = await self.db.get_search_participants(active_search['id'])
        map_url = await self.map_cache.get_map_url(participants)
        
        keyboard = [
            [InlineKeyboardButton("🔄 Обновить карту", callback_data="refresh_map")],
            [InlineKeyboardButton("« В меню карты", callback_data="map_menu")]
        ]
        
        await update.callback_query.message.edit_text(
            "🗺 Карта поиска\n\n"
            f"👥 Участников на карте: {len(participants)}\n"
            f"🔗 Ссылка на карту: {map_url}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return True

    async def _update_locations(self, context: ContextTypes.DEFAULT_TYPE):
        """Периодическое обновление координат"""
        job = context.job
        chat_id = job.context['chat_id']
        group_id = job.context['group_id']
        
        # Получаем обновленные координаты
        members = self.db.get_group_members_locations(group_id)
        
        # Генерируем новую карту
        map_file = self.map_service.generate_dynamic_map(members)
        
        if map_file:
            with open(f"temp/{map_file}", "rb") as f:
                await context.bot.send_document(
                    chat_id=chat_id,
                    document=f,
                    filename="map.html",
                    caption="🗺 Обновленная карта группы"
                )

    async def _auto_save_track(self, user_id: int, context: ContextTypes.DEFAULT_TYPE):
        """Автоматическое сохранение и сжатие трека"""
        track_data = self.active_tracks[user_id]
        compressed_points = self.track_compressor.compress_track(track_data['points'])
        
        # Сохраняем сжатый трек
        success = self.db.update_track_points(
            track_data['track_id'],
            compressed_points,
            calculate_distance=True
        )
        
        if success:
            # Очищаем буфер точек
            track_data['points'] = []
            await context.bot.send_message(
                chat_id=user_id,
                text="✅ Трек автоматически сохранен и оптимизирован"
            )

    async def show_track_export_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Меню экспорта трека"""
        track_id = context.user_data.get('selected_track_id')
        if not track_id:
            await update.callback_query.message.edit_text(
                "❌ Сначала выберите трек для экспорта.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« Назад", callback_data="track_list")
                ]])
            )
            return
        
        keyboard = [
            [InlineKeyboardButton("📍 GPX формат", callback_data=f"export_gpx_{track_id}")],
            [InlineKeyboardButton("🗺 KML формат", callback_data=f"export_kml_{track_id}")],
            [InlineKeyboardButton("📊 JSON формат", callback_data=f"export_json_{track_id}")],
            [InlineKeyboardButton("📑 CSV формат", callback_data=f"export_csv_{track_id}")],
            [InlineKeyboardButton("« Назад", callback_data="track_view")]
        ]
        
        await update.callback_query.message.edit_text(
            "📤 Выберите формат для экспорта трека:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def handle_track_export(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка экспорта трека"""
        query = update.callback_query
        format_type, track_id = query.data.split('_')[1:]
        
        track_data = self.db.get_track(int(track_id))
        if not track_data:
            await query.message.edit_text("❌ Трек не найден.")
            return
        
        try:
            # Компрессия трека перед экспортом
            compressed_points = self.track_compressor.compress_track(
                json.loads(track_data['points_json'])
            )
            
            # Подготовка данных для экспорта
            export_data = {
                'name': f"Track_{track_id}",
                'description': track_data.get('description', ''),
                'points': compressed_points,
                'metadata': track_data.get('metadata', {})
            }
            
            # Экспорт в выбранный формат
            exported_data = self.track_exporter.export_track(export_data, format_type)
            
            # Отправка файла
            filename = f"track_{track_id}.{format_type}"
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=exported_data,
                filename=filename,
                caption=f"🗺 Трек экспортирован в формат {format_type.upper()}"
            )
            
        except Exception as e:
            logging.error(f"Export error: {e}")
            await query.message.edit_text(
                "❌ Ошибка при экспорте трека. Попробуйте другой формат."
            )

    async def _update_gps_status_ui(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                  gps_status: dict):
        """Обновление UI с индикацией GPS статуса"""
        status_messages = {
            'ok': "📍 GPS сигнал стабильный",
            'signal_loss': "⚠️ Слабый GPS сигнал",
            'critical_signal_loss': "❌ Потеря GPS сигнала"
        }
        
        keyboard = []
        message = status_messages.get(gps_status['status'], "❓ Неизвестный статус GPS")
        
        if gps_status['status'] != 'ok':
            message += f"\nПоследняя известная позиция: {gps_status['duration']:.0f} сек. назад"
            keyboard.append([InlineKeyboardButton("📍 Отправить последнюю позицию", 
                                                callback_data="send_last_location")])
        
        keyboard.append([InlineKeyboardButton("« В меню карты", callback_data="map_menu")])
        
        await update.message.reply_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def analyze_track(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Анализ трека и отображение статистики"""
        track_id = context.user_data.get('selected_track_id')
        if not track_id:
            await update.callback_query.message.edit_text(
                "❌ Сначала выберите трек для анализа.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« Назад", callback_data="track_list")
                ]])
            )
            return
        
        track = self.db.get_track(track_id)
        if not track:
            await update.callback_query.message.edit_text("❌ Трек не найден.")
            return
        
        points = json.loads(track['points_json'])
        analyzer = TrackAnalyzer()
        stats = analyzer.analyze_track(points)
        
        # Форматируем статистику для отображения
        stats_text = (
            f"📊 Анализ трека #{track_id}\n\n"
            f"📏 Расстояние: {stats['total_distance']} км\n"
            f"⏱ Общее время: {stats['duration']}\n"
            f"🏃‍♂️ Время в движении: {stats['moving_time']}\n"
            f"⚡️ Средняя скорость: {stats['avg_speed']} км/ч\n"
            f"🚀 Максимальная скорость: {stats['max_speed']} км/ч\n"
            f"📈 Набор высоты: {stats['elevation_gain']} м\n"
            f"📉 Потеря высоты: {stats['elevation_loss']} м\n"
            f"⏱ Темп: {stats['pace']} мин/км\n\n"
            f"📍 Точек: {stats['points_count']}\n"
            f"🕒 Начало: {datetime.fromisoformat(stats['start_time']).strftime('%H:%M:%S')}\n"
            f"🕒 Конец: {datetime.fromisoformat(stats['end_time']).strftime('%H:%M:%S')}"
        )
        
        keyboard = [
            [InlineKeyboardButton("📊 Детальный анализ", callback_data=f"track_segments_{track_id}")],
            [InlineKeyboardButton("📍 Показать на карте", callback_data=f"track_view_{track_id}")],
            [InlineKeyboardButton("« Назад", callback_data="track_list")]
        ]
        
        await update.callback_query.message.edit_text(
            stats_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def handle_live_tracking_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Включение live-трекинга"""
        user_id = update.effective_user.id
        
        if user_id in self.live_tracking_users:
            await update.callback_query.message.edit_text(
                "❌ Live-трекинг уже включен",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« Назад", callback_data="map_menu")
                ]])
            )
            return
        
        self.live_tracking_users.add(user_id)
        
        # Запускаем периодическое обновление позиции
        context.job_queue.run_repeating(
            self.update_live_position,
            interval=30,  # каждые 30 секунд
            first=1,
            context=user_id
        )
        
        keyboard = [
            [InlineKeyboardButton("⏹ Остановить трекинг", callback_data="live_tracking_stop")],
            [InlineKeyboardButton("« Назад", callback_data="map_menu")]
        ]
        
        await update.callback_query.message.edit_text(
            "✅ Live-трекинг активирован\n"
            "Ваша позиция будет обновляться каждые 30 секунд\n"
            "Для остановки нажмите кнопку ниже",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def handle_search_sectors(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Управление поисковыми секторами"""
        query = update.callback_query
        user_id = update.effective_user.id
        
        # Проверяем, является ли пользователь координатором
        user = self.db.get_user(user_id)
        if not user.get('is_coordinator'):
            await query.message.edit_text(
                "❌ Доступ к управлению секторами имеют только координаторы",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« Назад", callback_data="map_menu")
                ]])
            )
            return
        
        # Получаем активные операции пользователя
        active_operations = self.db.get_active_operations(coordinator_id=user_id)
        
        keyboard = [
            [InlineKeyboardButton("➕ Создать сектор", callback_data="sector_create")],
            [InlineKeyboardButton("📋 Список секторов", callback_data="sector_list")],
            [InlineKeyboardButton("🗺 Карта секторов", callback_data="sector_map")],
            [InlineKeyboardButton("« Назад", callback_data="map_menu")]
        ]
        
        await query.message.edit_text(
            "🔍 Управление поисковыми секторами\n\n"
            f"Активных операций: {len(active_operations)}\n"
            "Выберите действие:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def update_live_position(self, context: ContextTypes.DEFAULT_TYPE):
        """Обновление live-позиции пользователя"""
        user_id = context.job.context
        
        # Получаем последнюю позицию из активного трека или запрашиваем новую
        position = self.get_last_position(user_id)
        if position:
            self.db.save_live_position(
                user_id=user_id,
                latitude=position['latitude'],
                longitude=position['longitude'],
                altitude=position.get('altitude'),
                accuracy=position.get('accuracy')
            )

    async def handle_offline_maps(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик меню офлайн-карт"""
        keyboard = [
            [InlineKeyboardButton("📥 Скачать область", callback_data="download_area")],
            [InlineKeyboardButton("📱 Офлайн-карты", callback_data="show_offline_maps")],
            [InlineKeyboardButton("🗺 Мои маршруты", callback_data="offline_routes")],
            [InlineKeyboardButton("🔄 Синхронизировать", callback_data="sync_data")],
            [InlineKeyboardButton("« Назад", callback_data="map_menu")]
        ]
        
        await update.callback_query.message.edit_text(
            "🗺 Управление офлайн-картами\n\n"
            "• Скачайте карты для работы без интернета\n"
            "• Просматривайте сохраненные маршруты\n"
            "• Синхронизируйте данные при появлении сети",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def handle_download_area(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик скачивания области карты"""
        context.user_data['state'] = 'awaiting_location'
        
        keyboard = [
            [InlineKeyboardButton("📍 Отправить локацию", callback_data="send_location")],
            [InlineKeyboardButton("« Назад", callback_data="offline_maps")]
        ]
        
        await update.callback_query.message.edit_text(
            "📍 Отправьте локацию центра области для скачивания.\n\n"
            "После этого вы сможете выбрать радиус и масштаб карт.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def process_area_download(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка скачивания области после получения локации"""
        if not update.message.location:
            return
        
        lat = update.message.location.latitude
        lon = update.message.location.longitude
        
        # Сохраняем координаты в контексте
        context.user_data['download_center'] = (lat, lon)
        
        keyboard = [
            [
                InlineKeyboardButton("1 км", callback_data="download_1km"),
                InlineKeyboardButton("3 км", callback_data="download_3km"),
                InlineKeyboardButton("5 км", callback_data="download_5km")
            ],
            [InlineKeyboardButton("« Назад", callback_data="offline_maps")]
        ]
        
        await update.message.reply_text(
            "📏 Выберите радиус области для скачивания:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def show_operation_map(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ комплексной карты операции"""
        query = update.callback_query
        operation_id = int(query.data.split('_')[-1])
        
        # Генерируем карту
        map_file = await self.map_service.generate_operational_map(operation_id)
        
        if map_file:
            # Отправляем файл с картой
            with open(map_file, "rb") as f:
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=f,
                    filename="operation_map.html",
                    caption="🗺 Интерактивная карта операции"
                )
            
            # Добавляем кнопки управления
            keyboard = [
                [
                    InlineKeyboardButton("🔄 Обновить", callback_data=f"map_refresh_{operation_id}"),
                    InlineKeyboardButton("📍 Моя позиция", callback_data="send_location")
                ],
                [
                    InlineKeyboardButton("🎯 Добавить точку", callback_data=f"add_point_{operation_id}"),
                    InlineKeyboardButton("⚡️ Отправить SOS", callback_data=f"send_sos_{operation_id}")
                ],
                [InlineKeyboardButton("« Назад", callback_data="map_menu")]
            ]
            
            await query.message.edit_text(
                "🗺 Карта операции\n\n"
                "• Используйте контрол слоев для управления отображением\n"
                "• Красные маркеры - важные точки\n"
                "• Тепловая карта показывает активность групп\n"
                "• Цвета секторов отображают их статус",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await query.message.edit_text(
                "❌ Не удалось сгенерировать карту. Попробуйте позже.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« Назад", callback_data="map_menu")
                ]])
            )

    async def handle_map_refresh(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка обновления карты"""
        query = update.callback_query
        operation_id = int(query.data.split('_')[-1])
        
        await query.answer("🔄 Обновление карты...")
        await self.show_operation_map(update, context)

    async def handle_auto_refresh_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Настройка автообновления карты"""
        query = update.callback_query
        operation_id = context.user_data.get('current_operation_id')
        
        if not operation_id:
            await query.answer("❌ Сначала выберите операцию")
            return
        
        keyboard = [
            [
                InlineKeyboardButton("1 мин", callback_data=f"map_refresh_60_{operation_id}"),
                InlineKeyboardButton("5 мин", callback_data=f"map_refresh_300_{operation_id}"),
                InlineKeyboardButton("10 мин", callback_data=f"map_refresh_600_{operation_id}")
            ],
            [InlineKeyboardButton("❌ Выключить", callback_data=f"map_refresh_stop_{operation_id}")],
            [InlineKeyboardButton("« Назад", callback_data="coord_map_settings")]
        ]
        
        await query.message.edit_text(
            "⚙️ Настройка автообновления\n\n"
            "Выберите интервал обновления карты:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def handle_refresh_interval(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Установка интервала автообновления"""
        query = update.callback_query
        data = query.data.split('_')
        interval = int(data[2])
        operation_id = int(data[3])
        
        if data[1] == 'stop':
            await self.map_service.stop_auto_refresh(operation_id)
            await query.answer("Автообновление выключено")
        else:
            await self.map_service.start_auto_refresh(
                operation_id, 
                context, 
                update.effective_chat.id, 
                interval
            )
            await query.answer(f"Автообновление включено ({interval} сек)")
        
        await self.show_map_settings(update, context)

    async def show_map_type_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Настройки типа карты"""
        keyboard = [
            [
                InlineKeyboardButton("🗺 Яндекс Карты", callback_data="map_type_yandex"),
                InlineKeyboardButton("🌍 OpenStreetMap", callback_data="map_type_osm")
            ],
            [
                InlineKeyboardButton("📡 Спутник", callback_data="map_type_satellite"),
                InlineKeyboardButton("🏷 Гибрид", callback_data="map_type_hybrid")
            ],
            [InlineKeyboardButton("« Назад", callback_data="coord_map_settings")]
        ]
        
        await update.callback_query.message.edit_text(
            "🗺 Выберите тип карты:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def handle_map_export(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка экспорта карты"""
        query = update.callback_query
        operation_id = context.user_data.get('current_operation_id')
        
        if not operation_id:
            await query.answer("❌ Сначала выберите операцию")
            return
        
        keyboard = [
            [
                InlineKeyboardButton("📍 GPX", callback_data=f"export_gpx_{operation_id}"),
                InlineKeyboardButton("🗺 KML", callback_data=f"export_kml_{operation_id}")
            ],
            [
                InlineKeyboardButton("📊 JSON", callback_data=f"export_json_{operation_id}"),
                InlineKeyboardButton("📑 CSV", callback_data=f"export_csv_{operation_id}")
            ],
            [InlineKeyboardButton("« Назад", callback_data="coord_map_settings")]
        ]
        
        await query.message.edit_text(
            "📤 Выберите формат экспорта:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
