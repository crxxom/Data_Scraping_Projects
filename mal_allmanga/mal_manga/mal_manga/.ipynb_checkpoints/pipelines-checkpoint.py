# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class MalMangaPipeline:
    def process_item(self, item, spider):
        
        adapter = ItemAdapter(item)
    
        int_columns = ['Volumes', 'Chapters', 'Members', 'Score_10', 'Score_9', 'Score_8', 'Score_7', 'Score_6',
                        'Score_5', 'Score_4', 'Score_3', 'Score_2', 'Score_1', 'Favorited', 'Reading', 'Completed',
                      'On_Hold', 'Dropped', 'Plan_to_Read', 'Score']
        for column in int_columns:
            if column == 'Score':
                value = adapter.get(column)
                if value and value != 'Unknown':
                    adapter[column] = float(value.replace(',','').replace(',',''))
                else:
                    adapter[column] = None
            else:
                value = adapter.get(column)
                if value and value != 'Unknown':
                    adapter[column] = int(value.replace(',','').replace(',',''))
                else:
                    adapter[column] = None
        
        ranks = ['Ranked', 'Popularity']
        for rank in ranks:
            ranking = adapter.get(rank)
            if ranking and value != 'Unknown':
                adapter[rank] = int(ranking[1:].replace(',','').replace(',',''))
            else:
                adapter[rank] = None
                
        return item
