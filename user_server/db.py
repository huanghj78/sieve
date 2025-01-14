from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('mysql+pymysql://root:dr3645DRG@localhost:3306/chaos')
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


# def init_db():
#     # 在这里导入定义模型所需要的所有模块，这样它们就会正确的注册在
#     # 元数据上。否则你就必须在调用 init_db() 之前导入它们。
#     from models.laboratory import Laboratory
#     Base.metadata.create_all(bind=engine)
#     lab = Laboratory("lab1", "1 mins ago", "11111")
#     db_session.add(lab)
#     db_session.commit()
#     db_session.remove()
