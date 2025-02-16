import matplotlib.pyplot as plt
import io
import base64
from typing import List, Dict

class StatsVisualizer:
    def __init__(self):
        self.plt = plt
        # Убираем проблемную строку plt.style.use('seaborn')
        
    def create_activity_chart(self, data: List[Dict]) -> str:
        """Создание графика активности"""
        plt.figure(figsize=(10, 6))
        
        dates = [d['date'] for d in data]
        values = [d['value'] for d in data]
        
        plt.plot(dates, values, marker='o')
        plt.title('Активность за период')
        plt.xlabel('Дата')
        plt.ylabel('Количество операций')
        plt.xticks(rotation=45)
        
        return self._get_plot_image()

    def create_pie_chart(self, data: Dict[str, float], 
                        title: str = "Распределение") -> str:
        """Создание круговой диаграммы"""
        plt.figure(figsize=(8, 8))
        
        plt.pie(data.values(), labels=data.keys(), autopct='%1.1f%%')
        plt.title(title)
        
        return self._get_plot_image()

    def create_bar_chart(self, data: Dict[str, float], 
                        title: str = "Статистика",
                        xlabel: str = "",
                        ylabel: str = "") -> str:
        """Создание столбчатой диаграммы"""
        plt.figure(figsize=(10, 6))
        
        plt.bar(data.keys(), data.values())
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.xticks(rotation=45)
        
        return self._get_plot_image()

    def create_progress_chart(self, current: float, 
                            total: float, 
                            title: str = "Прогресс") -> str:
        """Создание диаграммы прогресса"""
        plt.figure(figsize=(8, 3))
        
        progress = (current / total) * 100
        plt.barh([''], [progress], color='green')
        plt.barh([''], [100-progress], left=[progress], color='lightgray')
        
        plt.title(title)
        plt.xlabel('Процент выполнения')
        
        # Добавляем текст с процентами
        plt.text(progress/2, 0, f'{progress:.1f}%', 
                ha='center', va='center')
        
        return self._get_plot_image()

    def _get_plot_image(self) -> str:
        """Преобразование графика в base64 строку"""
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()  # Очищаем текущий график
        
        # Кодируем изображение в base64
        graphic = base64.b64encode(image_png)
        return graphic.decode('utf-8')
