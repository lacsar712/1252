# -*- coding: utf-8 -*-
"""
数据库初始化脚本 - 填充演示数据
"""
import logging
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from models import Base, User, Book, Author, Publisher
from auth import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db():
    """初始化数据库表"""
    Base.metadata.create_all(bind=engine)
    logger.info("数据库表创建成功")


def seed_data():
    """填充演示数据"""
    db = SessionLocal()
    try:
        # 检查是否已有数据
        if db.query(User).count() > 0:
            logger.info("数据库已有数据，跳过初始化")
            return

        # 创建管理员用户
        admin = User(
            username="admin",
            email="admin@bookstore.com",
            hashed_password=get_password_hash("123456"),
            is_admin=True,
            is_active=True
        )
        db.add(admin)

        # 创建普通用户
        user = User(
            username="user",
            email="user@bookstore.com",
            hashed_password=get_password_hash("123456"),
            is_admin=False,
            is_active=True
        )
        db.add(user)

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
        
        # 创建示例出版社
        publishers = [
            Publisher(
                name="人民邮电出版社",
                location="北京市",
                founded_year=1953,
                website="https://www.ryjiaoyu.com",
                description="人民邮电出版社成立于1953年，是工业和信息化部主管的大型专业出版社，致力于科技、教育、大众等领域的出版工作。",
                logo="https://via.placeholder.com/200x200/f59e0b/ffffff?text=RMYD",
                is_active=True
            ),
            Publisher(
                name="机械工业出版社",
                location="北京市",
                founded_year=1952,
                website="https://www.cmpbook.com",
                description="机械工业出版社成立于1952年，是国内最大的科技出版社之一，以出版科技、教育、经管类图书著称。",
                logo="https://via.placeholder.com/200x200/3b82f6/ffffff?text=JXGY",
                is_active=True
            ),
            Publisher(
                name="电子工业出版社",
                location="北京市",
                founded_year=1982,
                website="https://www.phei.com.cn",
                description="电子工业出版社成立于1982年，是国内权威的电子信息类专业出版社，致力于电子信息、计算机等领域的出版。",
                logo="https://via.placeholder.com/200x200/10b981/ffffff?text=DZGY",
                is_active=True
            ),
            Publisher(
                name="作家出版社",
                location="北京市",
                founded_year=1953,
                website="https://www.zuojia.net.cn",
                description="作家出版社成立于1953年，是中国作家协会直属的国家级文学专业出版社，以出版当代文学作品为主。",
                logo="https://via.placeholder.com/200x200/ef4444/ffffff?text=ZJCB",
                is_active=True
            ),
            Publisher(
                name="重庆出版社",
                location="重庆市",
                founded_year=1950,
                website="https://www.cqph.com",
                description="重庆出版社成立于1950年，是重庆出版集团旗下的综合性出版社，出版范围涵盖社科、文学、科技等多个领域。",
                logo="https://via.placeholder.com/200x200/8b5cf6/ffffff?text=CQCB",
                is_active=True
            )
        ]
        
        for publisher in publishers:
            db.add(publisher)
        
        db.flush()
        
        # 创建作者映射字典
        author_map = {author.name: author for author in authors}
        
        # 创建出版社映射字典
        publisher_map = {publisher.name: publisher for publisher in publishers}
        
        # 创建示例图书并关联作者和出版社
        books = [
            Book(
                title="Python编程：从入门到实践",
                author="Eric Matthes",
                publisher="人民邮电出版社",
                publisher_id=publisher_map["人民邮电出版社"].id,
                isbn="9787115428028",
                price=89.00,
                stock=50,
                description="一本Python入门经典书籍，适合编程初学者学习Python的基础知识和项目实践。",
                cover_image="/api/static/images/python_crash_course.png",
                category="编程技术",
                authors=[author_map["Eric Matthes"]]
            ),
            Book(
                title="JavaScript高级程序设计",
                author="Nicholas C. Zakas",
                publisher="人民邮电出版社",
                publisher_id=publisher_map["人民邮电出版社"].id,
                isbn="9787115545381",
                price=129.00,
                stock=35,
                description="JavaScript领域的经典之作，全面深入地介绍了JavaScript语言的核心概念和高级特性。",
                cover_image="/api/static/images/s33703494.jpg",
                category="编程技术",
                authors=[author_map["Nicholas C. Zakas"]]
            ),
            Book(
                title="深入理解计算机系统",
                author="Randal E. Bryant",
                publisher="机械工业出版社",
                publisher_id=publisher_map["机械工业出版社"].id,
                isbn="9787111544937",
                price=139.00,
                stock=20,
                description="从程序员的视角讲解计算机系统的组成与运作原理，是计算机专业学生的必读书目。",
                cover_image="/api/static/images/s29195878.jpg",
                category="计算机基础",
                authors=[author_map["Randal E. Bryant"]]
            ),
            Book(
                title="算法导论",
                author="Thomas H. Cormen",
                publisher="机械工业出版社",
                publisher_id=publisher_map["机械工业出版社"].id,
                isbn="9787111407010",
                price=128.00,
                stock=25,
                description="全面介绍了现代计算机算法的各种概念和技术，是算法学习的权威教材。",
                cover_image="/api/static/images/s25648004.jpg",
                category="计算机基础",
                authors=[author_map["Thomas H. Cormen"]]
            ),
            Book(
                title="代码整洁之道",
                author="Robert C. Martin",
                publisher="人民邮电出版社",
                publisher_id=publisher_map["人民邮电出版社"].id,
                isbn="9787115216878",
                price=59.00,
                stock=40,
                description="软件工程领域的经典著作，讲述如何写出整洁、可维护的高质量代码。",
                cover_image="/api/static/images/s4103991.jpg",
                category="软件工程",
                authors=[author_map["Robert C. Martin"]]
            ),
            Book(
                title="设计模式：可复用面向对象软件的基础",
                author="Erich Gamma",
                publisher="机械工业出版社",
                publisher_id=publisher_map["机械工业出版社"].id,
                isbn="9787111618331",
                price=79.00,
                stock=30,
                description="GOF四人组的经典之作，系统讲解23种设计模式，是软件设计的必读书籍。",
                cover_image="/api/static/images/design_patterns.png",
                category="软件工程",
                authors=[author_map["Erich Gamma"]]
            ),
            Book(
                title="Vue.js设计与实现",
                author="霍春阳",
                publisher="人民邮电出版社",
                publisher_id=publisher_map["人民邮电出版社"].id,
                isbn="9787115583864",
                price=89.00,
                stock=45,
                description="深入解析Vue.js 3的设计原理与实现细节，帮助开发者理解框架内部机制。",
                cover_image="/api/static/images/vue_design.png",
                category="前端开发",
                authors=[author_map["霍春阳"]]
            ),
            Book(
                title="React进阶实战",
                author="徐超",
                publisher="电子工业出版社",
                publisher_id=publisher_map["电子工业出版社"].id,
                isbn="9787121350627",
                price=79.00,
                stock=28,
                description="React开发的进阶指南，涵盖Hooks、性能优化、状态管理等核心主题。",
                cover_image="/api/static/images/react_advanced.png",
                category="前端开发",
                authors=[author_map["徐超"]]
            ),
            Book(
                title="MySQL必知必会",
                author="Ben Forta",
                publisher="人民邮电出版社",
                publisher_id=publisher_map["人民邮电出版社"].id,
                isbn="9787115313980",
                price=39.00,
                stock=60,
                description="MySQL入门经典，以简洁明了的方式介绍SQL语言和MySQL数据库的使用。",
                cover_image="/api/static/images/mysql_must_know.png",
                category="数据库",
                authors=[author_map["Ben Forta"]]
            ),
            Book(
                title="Redis设计与实现",
                author="黄健宏",
                publisher="机械工业出版社",
                publisher_id=publisher_map["机械工业出版社"].id,
                isbn="9787111464747",
                price=79.00,
                stock=35,
                description="深入剖析Redis内部实现原理，是理解Redis设计思想的权威书籍。",
                cover_image="/api/static/images/s27297117.jpg",
                category="数据库",
                authors=[author_map["黄健宏"]]
            ),
            Book(
                title="活着",
                author="余华",
                publisher="作家出版社",
                publisher_id=publisher_map["作家出版社"].id,
                isbn="9787506365437",
                price=45.00,
                stock=80,
                description="余华的代表作，讲述一个人历经世间沧桑和磨难的故事，文字朴实而震撼人心。",
                cover_image="/api/static/images/s29053580.jpg",
                category="文学小说",
                authors=[author_map["余华"]]
            ),
            Book(
                title="三体",
                author="刘慈欣",
                publisher="重庆出版社",
                publisher_id=publisher_map["重庆出版社"].id,
                isbn="9787536692930",
                price=68.00,
                stock=55,
                description="中国科幻文学里程碑之作，雨果奖获奖作品，展现宇宙文明的宏大叙事。",
                cover_image="/api/static/images/s28357056.jpg",
                category="科幻小说",
                authors=[author_map["刘慈欣"]]
            )
        ]
        
        for book in books:
            db.add(book)
        
        db.commit()
        logger.info("演示数据填充成功")
        logger.info(f"  - 创建用户: admin (密码: 123456, 管理员)")
        logger.info(f"  - 创建用户: user (密码: 123456, 普通用户)")
        logger.info(f"  - 创建作者: {len(authors)} 位")
        logger.info(f"  - 创建出版社: {len(publishers)} 家")
        logger.info(f"  - 创建图书: {len(books)} 本")
        
    except Exception as e:
        logger.error(f"数据填充失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    seed_data()
