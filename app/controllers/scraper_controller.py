import queue
from app.engines.scraper_engine import ScraperEngine 
from app.engines.scraper_worker import ScraperWorker

class ScraperController:
    def __init__(self, *args, **kwargs):
        self.engine = ScraperEngine()
        self.msg_queue = queue.Queue()
        
        # Buffer to hold data before sending to Main Data Tab
        self.scraped_data_buffer = []
        
        # Callback function to update UI (Observer pattern)
        self.on_data_update = None

    def start_scraping_task(self, url):
        return self.start_bulk_scraping([url])

    def start_bulk_scraping(self, url_list):
        if not url_list:
            return "Erro: Lista vazia"
        worker = ScraperWorker(url_list, self.engine, self.msg_queue)
        worker.start()
        return "Coleta iniciada"

    def get_queue(self):
        return self.msg_queue

    def add_scraped_result(self, data):
        """Adds a single result dict to the buffer and notifies UI"""
        self.scraped_data_buffer.append(data)
        if self.on_data_update:
            self.on_data_update()

    def get_buffer(self):
        return self.scraped_data_buffer
    
    def clear_buffer(self):
        self.scraped_data_buffer = []
        if self.on_data_update:
            self.on_data_update()
            
    def register_observer(self, callback):
        self.on_data_update = callback