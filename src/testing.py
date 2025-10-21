
from src.city_center_scrap import scrap_citycenter
link = 'https://citycenter.jo/gaming/gaming-cpu-and-processor/intel-new-core-ultra-7-265kf-2'
# print(link)

x = scrap_citycenter(link)

for i in x:
    print(i)