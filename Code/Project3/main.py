
import pandas as pd
from functools import reduce
import networkx as nx
import matplotlib.pyplot as plt
import json
import numpy as np

def data_precess():
    data = pd.read_csv('owid-covid-data.csv')
    #data = pd.read_csv('https://covid.ourworldindata.org/data/owid-covid-data.csv')
    # 保留最新数据
    d1 = data.drop_duplicates(subset=['iso_code'], keep='last')
    d1 = d1[['iso_code', 'location', 'continent', 'total_deaths_per_million', 'aged_65_older']]
    d1 = d1.sort_values(by='iso_code')
    
    # 计算疫苗接种率最大值和控管指数平均值
    d2 = data.groupby('iso_code')['people_fully_vaccinated_per_hundred'].max()
    d3 = data.groupby('iso_code')['stringency_index'].mean()

    # 提取国家经纬度数据
    with open('allCountriesGeojson.json', encoding='utf-8') as f:
        country_loc = json.load(f)
    location = pd.json_normalize(country_loc, 'features', 
                            ['id', ['properties', 'latitude'], ['properties', 'longitude']],
                            meta_prefix = '_',
                            errors='ignore')
    location = location[['id','properties.latitude', 'properties.longitude']]
    location.columns=['iso_code','latitude', 'longitude']

    # 合并数据
    dfs = [d1, d2, d3, location]
    res = reduce(lambda x, y: pd.merge(x, y, on='iso_code', how='inner'), dfs)
    res = res.dropna()
    res = res.drop_duplicates(subset=['iso_code'], keep='last')
    res.to_csv('latest_info.csv')



def main():
    data_precess()
    data = pd.read_csv('latest_info.csv')
    data1 = data[['aged_65_older', 'stringency_index', 'people_fully_vaccinated_per_hundred']]
    
    G = nx.Graph()
    G.add_nodes_from(data['iso_code'])

    pos = {}
    node_size = []
    node_color = []
    for i in range(len(data)):
        # 结点坐标：经纬度   大小：死亡人数比例
        pos[data['iso_code'][i]] = [data['longitude'][i], data['latitude'][i]]
        node_size.append(data['total_deaths_per_million'][i]*0.05)
        # 结点颜色：所在大洲
        if data['continent'][i] == 'Asia':
            node_color.append('green')
        elif data['continent'][i] == 'Europe':
            node_color.append('blue')
        elif data['continent'][i] == 'Africa':
            node_color.append('red')
        elif data['continent'][i] == 'North America':
            node_color.append('purple')
        elif data['continent'][i] == 'South America':
            node_color.append('orange')
        else:
            node_color.append('gold')
        '''
        # 根据'aged_65_older', 'stringency_index', 'people_fully_vaccinated_per_hundred'
        # 计算欧氏距离，加边
        for j in range(i+1, len(data)):
            if np.linalg.norm(data1.loc[i] - data1.loc[j]) < 2:
               G.add_edge(data['iso_code'][i], data['iso_code'][j]) 
        '''

    # 画图
    nx.draw_networkx(G,pos,with_labels=False,alpha=0.5, node_size= node_size, node_color = node_color,
                    linewidths=1, width=1,edge_color='gray')
    
    plt.xlabel('longitude')
    plt.ylabel('Latitude')
    plt.show()
    
    
    


    
if __name__ == '__main__':
    main()