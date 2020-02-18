nboost  --uhost localhost --uport 9200 --search_route "/<index>/_search" --query_path url.query.q --topk_path url.query.size --default_topk 10 --choices_path body.hits.hits --cvalues_path _source.description

nboost-index --file ./docSearch-ws/data.BBC_news_dataset.csv --index_name bbc --delim , --id_col

python main.py --config ./config/config.yaml

