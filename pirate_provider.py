from PirateBayAPI import PirateBayAPI
from .base_provider import BaseProvider # Assuming this is where the interface is

class LumeEngineProvider(BaseProvider):
    async def search(self, query: str):
        # 1. Search using the library you have installed
        results = PirateBayAPI.Search(query) 
        
        if not results:
            return None
            
        # 2. Sort by seeds for the best streaming health
        results.sort(key=lambda x: int(x.seeds), reverse=True)
        top = results[0]
        
        # 3. Get the magnet link
        magnet = PirateBayAPI.Download(top.id)
        
        return {
            "title": top.name,
            "url": magnet,
            "size": top.size,
            "seeds": top.seeds
        }