from pymongo import MongoClient

# 创建一个MongoClient对象，连接到默认的主机和端口（localhost:27017）
client = MongoClient()

# 也可以指定主机和端口
# client = MongoClient('localhost', 27017)

# 选择或创建一个数据库
db = client['tgbot']

# 选择或创建一个集合
collection = db['users']
collection2 = db['channels']

# 插入单个文档
post = {"userid": 6653848637, "channels":["Odaily", "BlockBeats", "Foresight News"], "keywords":["ETH", "layer2", "BTC", "分片", "eip"]}
post_id = collection.insert_one(post).inserted_id

post = {"channelid":1919143832, "title":"messageloader", "users":[6653848637,]}
post_id = collection2.insert_one(post).inserted_id
# 插入多个文档
# posts = [
#     {"name": "Alice", "age": 25},
#     {"name": "Bob", "age": 27}
# ]
# collection.insert_many(posts)

# 查找集合中的所有文档
for doc in collection.find():
    print(doc)

# 查找特定文档
for doc in collection.find({"userid": 6653848637}):
    print(doc)
keywords = collection.find({"userid": 6653848637})[0]['keywords']
user = collection.find_one({"userid": 665384})
print(user)

