import psycopg2
from const import DBNAME, DBURL


def commit(func):
    def return_func(*args):
        conn = psycopg2.connect(DBURL)
        cursor = conn.cursor()
        try:
            func(*args, cursor=cursor)
            conn.commit()
            return True
        except Exception as e:
            print(e)
            return False
    return return_func


def select(func):
    def return_func(*args):
        conn = psycopg2.connect(DBURL)
        cursor = conn.cursor()
        return func(*args, cursor=cursor)
    return return_func


def select_only_one(func):
    func = select(func)

    def return_func(*args):
        try:
            return func(*args)[0]
        except:
            return None
    return return_func


class DataBase:
    def create(self):
        query_arr = list()
        query_arr.append("""                            
        CREATE TABLE users
        (
        id INT PRIMARY KEY,
        nickname VARCHAR (30) NOT NULL,
        email VARCHAR(120) UNIQUE NOT NULL,
        password VARCHAR(120) UNIQUE NOT NULL,
        avatar_path VARCHAR(120) DEFAULT 'img.png'
        );
        """)                                   # table users
        query_arr.append("""                            
        CREATE TABLE register_users
        (
        id SERIAL PRIMARY KEY,
        email VARCHAR(120) UNIQUE NOT NULL,
        password VARCHAR(120) UNIQUE NOT NULL,
        date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """)
        query_arr.append("""
        CREATE TABLE posts
        (
        id SERIAL PRIMARY KEY,
        description TEXT,
        id_user INT NOT NULL,
        likes INT DEFAULT 0,
        dislikes INT DEFAULT 0,
        date DATE DEFAULT CURRENT_DATE,
        
        FOREIGN KEY (id_user) REFERENCES users(id)
        );
        """)                                   # table posts
        query_arr.append("""
        CREATE TABLE photo_in_posts
        (
        img_path VARCHAR(120) NOT NULL UNIQUE,
        id_post INT NOT NULL,
        
        FOREIGN KEY (id_post) REFERENCES posts(id)
        );
        """)                                   # table photo_in_posts
        query_arr.append("""
        CREATE TABLE subscribes 
        (
        id_subscriber INT NOT NULL,
        id_subscribe_user INT NOT NULL,
        
        FOREIGN KEY (id_subscriber) REFERENCES users(id),
        FOREIGN KEY (id_subscribe_user) REFERENCES users(id)
        );
        """)                                   # table subscribes
        query_arr.append("""
        CREATE TABLE likes
        (
        id_post INT NOT NULL,
        id_user INT NOT NULL,
        FOREIGN KEY (id_user) REFERENCES users(id),
        FOREIGN KEY (id_post) REFERENCES posts(id)
        );
        """)                                   # table likes
        query_arr.append("""
        CREATE TABLE dislikes
        (
        id_post INT NOT NULL,
        id_user INT NOT NULL,
        FOREIGN KEY (id_user) REFERENCES users(id),
        FOREIGN KEY (id_post) REFERENCES posts(id)
        );
        """)                                   # table dislikes
        query_arr.append("""
        CREATE FUNCTION like_func()
        RETURNS trigger AS
        $$
        BEGIN
            IF NEW.id_post = (SELECT id_post FROM dislikes WHERE id_post = NEW.id_post AND id_user = NEW.id_user) THEN
                UPDATE posts
                SET dislikes = dislikes - 1
                WHERE id = NEW.id_post;
                DELETE FROM dislikes WHERE id_post = NEW.id_post AND id_user = NEW.id_user;
            END IF;
            IF (SELECT COUNT(*)  FROM likes WHERE id_post = NEW.id_post AND id_user = NEW.id_user) = 2 THEN
                UPDATE posts
                SET likes = likes - 1
                WHERE id = NEW.id_post;
                DELETE FROM likes WHERE id_post = NEW.id_post AND id_user = NEW.id_user;
            ELSE
                UPDATE posts 
                SET likes = likes + 1
                WHERE id = NEW.id_post;
            END IF;
            RETURN NEW;
            END;
        $$ 
        LANGUAGE 'plpgsql';
        """)                                   # function for likes
        query_arr.append("""
        CREATE FUNCTION dislike_func()
        RETURNS trigger AS
        $$
        BEGIN
            IF NEW.id_post = (SELECT id_post FROM likes WHERE id_post = NEW.id_post AND id_user = NEW.id_user) THEN
                UPDATE posts
                SET likes = likes - 1
                WHERE id = NEW.id_post;
                DELETE FROM likes WHERE id_post = NEW.id_post AND id_user = NEW.id_user;
            END IF;
            IF (SELECT COUNT(*)  FROM dislikes WHERE id_post = NEW.id_post AND id_user = NEW.id_user) = 2 THEN
                UPDATE posts
                SET dislikes = dislikes - 1
                WHERE id = NEW.id_post;
                DELETE FROM dislikes WHERE id_post = NEW.id_post AND id_user = NEW.id_user;
            ELSE
                UPDATE posts 
                SET dislikes = dislikes + 1
                WHERE id = NEW.id_post;
            END IF;
            RETURN NEW;
            END;
        $$ 
        LANGUAGE 'plpgsql';
        """)                                   # function for dislikes
        query_arr.append("""
        CREATE TRIGGER like_trigger AFTER INSERT ON likes
        FOR EACH ROW
        EXECUTE PROCEDURE like_func();
        """)                                   # like trigger
        query_arr.append("""
        CREATE TRIGGER dislike_trigger AFTER INSERT ON dislikes
        FOR EACH ROW
        EXECUTE PROCEDURE dislike_func();
        """)                                   # dislike trigger
        query_arr.append("""
        CREATE INDEX users_posts_id
        ON posts (id_user);
        """)                                   # index for faster searching post by id_user
        query_arr.append("""
        CREATE INDEX users_posts_date
        ON posts (date);
        """)                                   # index for faster searching post by date
        query_arr.append("""
        CREATE INDEX photo_in_posts_ind
        ON photo_in_posts (id_post);
        """)
        query_arr.append("""
        CREATE INDEX subscribes_id_subscriber
        ON subscribes (id_subscriber);
        """)
        query_arr.append("""
        CREATE INDEX subscribes_id_subscribe_user
        ON subscribes (id_subscribe_user);
        """)
        query_arr.append("""
        CREATE INDEX likes_ind
        ON likes (id_user, id_post);
        """)
        query_arr.append("""
        CREATE INDEX dislikes_ind
        ON dislikes (id_user ,id_post);
        """)
        query_arr.append("""
        CREATE TABLE news
        (
        id_user INT NOT NULL,
        id_post INT NOT NULL,
        FOREIGN KEY (id_user) REFERENCES users(id), 
        FOREIGN KEY (id_post) REFERENCES posts(id) 
        );
        """)
        query_arr.append("""
        CREATE INDEX news_index
        ON news (id_user, id_post);
        """)
        query_arr.append("""
        CREATE FUNCTION news_func()
        RETURNS TRIGGER AS 
        $$
        BEGIN
        INSERT INTO news(id_user,id_post) 
            (SELECT id_subscriber, NEW.id 
            FROM subscribes
            WHERE id_subscribe_user = NEW.id_user);
        RETURN NEW;
        END;
        $$ 
        LANGUAGE 'plpgsql';
        """)
        query_arr.append("""
        CREATE TRIGGER news_trigger AFTER INSERT ON posts
        FOR EACH ROW
        EXECUTE PROCEDURE news_func();
        """)
        conn = psycopg2.connect(DBURL)
        cursor = conn.cursor()
        create = True
        for query in query_arr:
            try:
                cursor.execute(query)
            except Exception as e:
                print(query)
                print()
                print(e)
                create = False
        if create:
            conn.commit()

    def drop_all(self):
        q1 = "DROP SCHEMA public CASCADE;"
        q2 = "CREATE SCHEMA public;"
        conn = psycopg2.connect(DBURL)
        cursor = conn.cursor()
        cursor.execute(q1)
        cursor.execute(q2)
        conn.commit()


    @commit
    def insert_user_to_register_users(self, email, password, cursor):
        cursor.execute(f"""
                INSERT INTO register_users (email, password)
                VALUES
                ('{email}','{password}');
                """)

    @commit
    def insert_user(self, id_user, nickname, email, password, cursor):
        cursor.execute(f"""
                INSERT INTO users(id, nickname, email, password)
                VALUES
                ({id_user}, '{nickname}', '{email}', '{password}');
                """)

    @select_only_one
    def get_id_reg_user_by_email_password(self, email, password, cursor):
        cursor.execute(f"""
                    SELECT id FROM register_users 
                    WHERE email = '{email}' AND password = '{password}';
                    """)
        return cursor.fetchall()[0]

    @commit
    def set_avatar(self, id_user, ava_path, cursor):
        cursor.execute(f"""
                UPDATE users
                SET avatar_path = '{ava_path}'
                WHERE id = {id_user};
                """)

    @select_only_one
    def get_user_by_email_password(self, email, password, cursor):
        cursor.execute(f"""
                SELECT * FROM users 
                WHERE email = '{email}' AND password = '{password}';
                """)
        return cursor.fetchall()

    @select_only_one
    def pop_reg_user_by_id(self, id_user, cursor):
        cursor.execute(f"""
                SELECT email, password FROM register_users
                WHERE id = {id_user};
                """)
        self.delele_reg_user_by_id(id_user)
        return cursor.fetchall()

    @commit
    def delele_reg_user_by_id(self, id_user, cursor):
        cursor.execute(f"""
                DELETE FROM register_users
                WHERE id = {id_user};
        """)

    @select_only_one
    def get_user_by_email(self, email, cursor):
        user = []
        cursor.execute(f"""
                SELECT * FROM users 
                WHERE email = '{email}';
                """)
        user.extend(cursor.fetchall())
        cursor.execute(f"""
                SELECT * FROM  register_users
                WHERE email = '{email}';
                """)
        user.extend(cursor.fetchall())
        return user

    @select_only_one
    def get_user_nickname(self, id_user, cursor):
        cursor.execute(f"""
                SELECT nickname FROM users 
                WHERE id = {id_user};
                """)
        return cursor.fetchall()[0]

    @select_only_one
    def get_user_by_password(self, password, cursor):
        user = []
        cursor.execute(f"""
                SELECT * FROM users 
                WHERE password = '{password[0:120]}';
                """)
        user.extend(cursor.fetchall())
        cursor.execute(f"""
                        SELECT * FROM users 
                        WHERE password = '{password[0:120]}';
                        """)
        user.extend(cursor.fetchall())
        return user

    @commit
    def insert_post(self, id_user, description, cursor):
        cursor.execute(f"""
              INSERT INTO posts(id_user, description)
              VALUES
              ({id_user},'{description}');
              """)

    @select_only_one
    def get_last_user_post_id(self, id_user, cursor):
        cursor.execute(f"""
              SELECT id FROM posts
              WHERE id_user = {id_user}
              ORDER BY date DESC
              LIMIT 1;
              """)
        return cursor.fetchall()[0]         # [0] because  cursor.fetchall() return (id,)

    @commit
    def insert_post_photo(self, id_post, img_path, cursor):
        cursor.execute(f"""
            INSERT INTO photo_in_posts (id_post, img_path)
            VALUES 
            ({id_post},'{img_path}');
            """)

    @select
    def get_posts_id_by_id_user(self, id_user, cursor):
        cursor.execute(f"""
            SELECT id FROM posts
            WHERE id_user = {id_user};
            """)
        return cursor.fetchall()

    @select_only_one
    def get_post_photo(self, id_post, cursor):
        cursor.execute(f"""
            SELECT img_path FROM photo_in_posts
            WHERE id_post = {id_post}
            LIMIT 1;
            """)
        return cursor.fetchall()[0]

    @select_only_one
    def get_post_by_id(self, id_post, cursor):
        cursor.execute(f"""
            SELECT p.id, p.description, p.id_user, p.likes, p.dislikes, p.date, 
                (SELECT u.nickname
                FROM users u
                WHERE p.id_user = u.id
                LIMIT 1)
            FROM posts p
            WHERE p.id = {id_post};
            """)
        return cursor.fetchall()

    @select
    def get_post_photos(self, id_post, cursor):
        cursor.execute(f"""
            SELECT img_path FROM photo_in_posts
            WHERE id_post = {id_post};
            """)
        return cursor.fetchall()

    @select_only_one
    def get_user_by_id(self, id_user, cursor):
        cursor.execute(f"""
            SELECT * FROM users
            WHERE id = {id_user};
            """)
        return cursor.fetchall()

    @commit
    def like_post(self, id_post, id_user, cursor):
        cursor.execute(f"""
            INSERT INTO likes (id_post,id_user)
            VALUES
            ({id_post},{id_user});
            """)

    @commit
    def dislike_post(self, id_post, id_user, cursor):
        cursor.execute(f"""
               INSERT INTO dislikes (id_post,id_user)
               VALUES
               ({id_post},{id_user});
               """)

    @select
    def get_subscribes(self, id_user, cursor):
        cursor.execute(f"""
                SELECT u.nickname, u.avatar_path, u.id,
                    (SELECT COUNT(*) FROM subscribes s1
                     WHERE s.id_subscribe_user = s1.id_subscribe_user),

                     (SELECT COUNT(*) FROM subscribes s1
                     WHERE s.id_subscribe_user = s1.id_subscriber),

                    (SELECT COUNT(*) FROM subscribes s1 
                    JOIN subscribes s2 ON s1.id_subscriber={id_user}
                    WHERE s2.id_subscriber = s.id_subscribe_user 
                    AND s1.id_subscribe_user = s2.id_subscribe_user),

                    (SELECT COUNT(*) FROM subscribes s1 
                    JOIN subscribes s2 ON s1.id_subscribe_user={id_user}
                    WHERE s2.id_subscribe_user = s.id_subscribe_user 
                    and s1.id_subscriber = s2.id_subscriber)

                FROM subscribes s 
                JOIN users u ON u.id = s.id_subscribe_user
                WHERE s.id_subscriber = {id_user}
                LIMIT 15;""")
        return cursor.fetchall()

    @select
    def get_subscribers(self, id_user, cursor):
        cursor.execute(f"""
                    SELECT u.nickname, u.avatar_path, u.id,
                    (SELECT COUNT(*) FROM subscribes s1
                     WHERE s.id_subscribe_user = s1.id_subscribe_user),

                     (SELECT COUNT(*) FROM subscribes s1
                     WHERE s.id_subscribe_user = s1.id_subscriber),

                    (SELECT COUNT(*) FROM subscribes s1 
                    JOIN subscribes s2 ON s1.id_subscriber={id_user}
                    WHERE s2.id_subscriber = s.id_subscriber 
                    AND s1.id_subscribe_user = s2.id_subscribe_user),

                    (SELECT COUNT(*) FROM subscribes s1 
                    JOIN subscribes s2 ON s1.id_subscribe_user={id_user}
                    WHERE s2.id_subscribe_user = s.id_subscriber 
                    and s1.id_subscriber = s2.id_subscriber)

                FROM subscribes s 
                JOIN users u ON u.id = s.id_subscriber
                WHERE s.id_subscribe_user = {id_user}
                LIMIT 15;""")
        return cursor.fetchall()

    @select_only_one
    def get_like(self, id_post, id_user, cursor):
        cursor.execute(f"""
            SELECT * FROM likes
            WHERE id_post = {id_post} AND id_user = {id_user}""")
        return cursor.fetchall()

    @select_only_one
    def get_dislike(self, id_post, id_user, cursor):
        cursor.execute(f"""
            SELECT * FROM dislikes
            WHERE id_post = {id_post} AND id_user = {id_user}""")
        return cursor.fetchall()

    @select
    def search_in_users_by_name(self, search, cursor):
        cursor.execute(f"""
            SELECT nickname, avatar_path, id 
            FROM users
            WHERE nickname LIKE '%{search}%'""")
        return cursor.fetchall()

    @select
    def get_news(self,id_user,cursor):
        cursor.execute(f"""
            SELECT n.id_post,(SELECT img_path 
                                FROM photo_in_posts pp 
                                WHERE pp.id_post = n.id_post LIMIT 1)
            FROM news n WHERE id_user={id_user} LIMIT 7;
            """)
        return cursor.fetchall()

    @select
    def get_user_posts(self, id_user, cursor):
        cursor.execute(f"""
            SELECT p.id, p.date, p.likes, p.dislikes,
                (SELECT pp.img_path 
                FROM photo_in_posts pp
                WHERE pp.id_post = p.id
                LIMIT 1)
            FROM posts p
            WHERE p.id_user = {id_user}
            """)
        return cursor.fetchall()

    def get_sub_and_posts_count(self,id_user):
        conn = psycopg2.connect(DBURL)
        cursor = conn.cursor()
        arr = []
        cursor.execute(f"""
            SELECT COUNT(*) FROM subscribes WHERE id_subscriber = {id_user};""")
        arr.append(cursor.fetchall()[0][0])
        cursor.execute(f"""
            SELECT COUNT(*) FROM subscribes WHERE id_subscribe_user = {id_user};""")
        arr.append(cursor.fetchall()[0][0])
        cursor.execute(f"""
            SELECT COUNT(*) FROM posts WHERE id_user = {id_user};""")
        arr.append(cursor.fetchall()[0][0])
        return arr

    @select_only_one
    def if_subscribe(self,id_current_user,id_user,cursor):
        cursor.execute(f"""
            SELECT * FROM subscribes WHERE id_subscriber = {id_current_user} AND id_subscribe_user = {id_user}""")
        return cursor.fetchall()

    @commit
    def delete_sub(self, id_user1, id_user2, cursor):
        cursor.execute(f"""
            DELETE FROM subscribes WHERE id_subscriber = {id_user1} AND id_subscribe_user = {id_user2};
        """)

    @commit
    def insert_sub(self, id_user1, id_user2, cursor):
        cursor.execute(f"""
            INSERT INTO subscribes (id_subscriber,id_subscribe_user)
            VALUES({id_user1},{id_user2});
        """)

    @commit
    def delete_new(self,id_user,id_post,cursor):
        cursor.execute(f"DELETE FROM news WHERE id_user = {id_user} AND id_post = {id_post}")

    @select
    def get_posts(self, cursor):
        cursor.execute("""
        SELECT p.id, 
            (SELECT pp.img_path
            FROM photo_in_posts pp
            WHERE pp.id_post = p.id 
            LIMIT 1)
        FROM posts p
        LIMIT 50""")
        return cursor.fetchall()

db = DataBase()



# SELECT s.id_subscribe_user,u.nickname, u.avatar_path, u.id,
# (SELECT COUNT(*) FROM subscribes s1 JOIN subscribes s2 ON s1.id_subscriber=1
# WHERE s2.id_subscriber = s.id_subscribe_user AND s1.id_subscribe_user = s2.id_subscribe_user),
#
# FROM subscribes s JOIN users u ON u.id = s.id_subscribe_user
# WHERE s.id_subscriber = 1
# LIMIT 15;
#
# (SELECT count(*) FROm subscribes s1 JOIN subscribes s2 ON s1.id_subscribe_user=1
# WHERE s2.id_subscribe_user = 3 aND s1.id_subscriber = s2.id_subscriber)
#
# (SELECT * FROm subscribes s1 JOIN subscribes s2 ON s1.id_subscribe_user=1
# WHERE s2.id_subscribe_user = 7 and s1.id_subscriber = s2.id_subscriber)
