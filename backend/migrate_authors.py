# -*- coding: utf-8 -*-
"""
迁移脚本 - 添加作者数据并关联到现有图书
"""
import logging
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from models import Base, Author, Book
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_authors():
    """添加作者数据并关联到现有图书"""
    db = SessionLocal()
    try:
        # 检查是否已有作者数据
        if db.query(Author).count() > 0:
            logger.info("数据库已有作者数据，跳过迁移")
            return

        logger.info("开始迁移作者数据...")

        # 创建示例作者
        authors = [
            Author(
                name="Eric Matthes",
                country="美国",
                birth_year=1975,
                bio="Python编程教育家，专注于编程入门教育，著有多部畅销编程书籍。",
                masterpieces="Python编程：从入门到实践",
                avatar="/api/static/images/s4103991.jpg",
                is_active=True
            ),
            Author(
                name="Nicholas C. Zakas",
                country="美国",
                birth_year=1978,
                bio="前端技术专家，曾任Yahoo前端工程师，著有多部JavaScript经典著作。",
                masterpieces="JavaScript高级程序设计",
                avatar="/api/static/images/s33703494.jpg",
                is_active=True
            ),
            Author(
                name="Randal E. Bryant",
                country="美国",
                birth_year=1952,
                bio="卡内基梅隆大学计算机科学教授，ACM Fellow，研究领域包括系统验证和形式化方法。",
                masterpieces="深入理解计算机系统",
                avatar="/api/static/images/s29195878.jpg",
                is_active=True
            ),
            Author(
                name="Thomas H. Cormen",
                country="美国",
                birth_year=1956,
                bio="达特茅斯学院计算机科学教授，算法领域权威专家。",
                masterpieces="算法导论",
                avatar="/api/static/images/s25648004.jpg",
                is_active=True
            ),
            Author(
                name="Robert C. Martin",
                country="美国",
                birth_year=1952,
                bio="软件开发大师，敏捷开发宣言签署人之一，被誉为『 Uncle Bob 』。",
                masterpieces="代码整洁之道、敏捷软件开发",
                avatar="/api/static/images/s29053580.jpg",
                is_active=True
            ),
            Author(
                name="Erich Gamma",
                country="瑞士",
                birth_year=1961,
                bio="GOF四人组之一，Eclipse平台主要开发者，设计模式领域权威。",
                masterpieces="设计模式：可复用面向对象软件的基础",
                avatar="/api/static/images/design_patterns.png",
                is_active=True
            ),
            Author(
                name="霍春阳",
                country="中国",
                birth_year=1990,
                bio="Vue.js核心团队成员，前端架构师，专注于框架设计与实现。",
                masterpieces="Vue.js设计与实现",
                avatar="/api/static/images/vue_design.png",
                is_active=True
            ),
            Author(
                name="徐超",
                country="中国",
                birth_year=1988,
                bio="资深前端工程师，拥有丰富的React开发经验，活跃于开源社区。",
                masterpieces="React进阶实战",
                avatar="/api/static/images/react_advanced.png",
                is_active=True
            ),
            Author(
                name="Ben Forta",
                country="美国",
                birth_year=1965,
                bio="Adobe技术总监，Web技术专家，著有多部数据库和Web开发畅销书籍。",
                masterpieces="MySQL必知必会",
                avatar="/api/static/images/mysql_must_know.png",
                is_active=True
            ),
            Author(
                name="黄健宏",
                country="中国",
                birth_year=1985,
                bio="Redis技术专家，Redis源码贡献者，著有多部Redis相关著作。",
                masterpieces="Redis设计与实现",
                avatar="/api/static/images/s27297117.jpg",
                is_active=True
            ),
            Author(
                name="余华",
                country="中国",
                birth_year=1960,
                bio="当代著名作家，北京师范大学教授，作品被翻译成30多种语言。",
                masterpieces="活着、许三观卖血记、兄弟",
                avatar="/api/static/images/s29053580.jpg",
                is_active=True
            ),
            Author(
                name="刘慈欣",
                country="中国",
                birth_year=1963,
                bio="科幻作家，中国科幻文学代表人物，雨果奖得主。",
                masterpieces="三体、球状闪电、流浪地球",
                avatar="/api/static/images/s28357056.jpg",
                is_active=True
            )
        ]

        for author in authors:
            db.add(author)

        db.flush()

        # 创建作者映射字典
        author_map = {author.name: author for author in authors}

        # 获取所有图书并关联作者
        books = db.query(Book).all()
        for book in books:
            if book.author in author_map:
                book.authors = [author_map[book.author]]
                logger.info(f"关联图书: {book.title} -> {book.author}")

        db.commit()
        logger.info(f"作者数据迁移完成，共添加 {len(authors)} 位作者，关联 {len(books)} 本图书")

    except Exception as e:
        logger.error(f"数据迁移失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    migrate_authors()
