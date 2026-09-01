from typing import Union

import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool

from data import config


class Database:

    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME,
            min_size=1,
            max_size=10,
            command_timeout=30,
        )

    async def execute(self, command, *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False
                      ):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    async def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users (
        id SERIAL PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL,
        username varchar(255) NULL,
        telegram_id BIGINT NOT NULL UNIQUE,
        from_lang varchar(5) NOT NULL DEFAULT 'uz',
        to_lang varchar(5) NOT NULL DEFAULT 'ru',
        is_active INT NOT NULL DEFAULT 1,
        last_seen TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """
        await self.execute(sql, execute=True)
        # Eski jadval bilan ham mos ishlash uchun xavfsiz migratsiya.
        await self.execute("ALTER TABLE Users ADD COLUMN IF NOT EXISTS last_seen TIMESTAMPTZ", execute=True)
        await self.execute("ALTER TABLE Users ALTER COLUMN from_lang SET DEFAULT 'uz'", execute=True)
        await self.execute("ALTER TABLE Users ALTER COLUMN to_lang SET DEFAULT 'ru'", execute=True)
        await self.execute("UPDATE Users SET from_lang='uz' WHERE from_lang IS NULL", execute=True)
        await self.execute("UPDATE Users SET to_lang='ru' WHERE to_lang IS NULL", execute=True)
        await self.execute("UPDATE Users SET last_seen=NOW() WHERE last_seen IS NULL", execute=True)

    async def create_table_admins(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Admins (
            telegram_id BIGINT PRIMARY KEY,
            added_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """
        await self.execute(sql, execute=True)

    async def seed_admins(self, admin_ids):
        # Faqat birinchi ishga tushishda .env dagi adminlar ko'chiriladi.
        # Keyingi restartlarda DB holati (jumladan admin o'chirilishi) saqlanadi.
        exists = await self.execute("SELECT EXISTS(SELECT 1 FROM Admins)", fetchval=True)
        if exists:
            return
        for admin_id in admin_ids:
            await self.add_admin(int(admin_id))

    async def create_table_chanel(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Channel (
        id SERIAL PRIMARY KEY,
        chanelll VARCHAR(101) NOT NULL,
        url varchar(101) NOT NULL
                );
        """
        await self.execute(sql, execute=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(),
                                                          start=1)
        ])
        return sql, tuple(parameters.values())

    async def add_user(self, full_name, telegram_id, username, type=1):
        """Foydalanuvchini yangilaydi, til tanlovini esa o'zgartirmaydi."""
        sql = """
        INSERT INTO users (full_name, telegram_id, username, is_active, last_seen)
        VALUES($1, $2, $3, $4, NOW())
        ON CONFLICT (telegram_id) DO UPDATE SET
            full_name=EXCLUDED.full_name,
            username=EXCLUDED.username,
            is_active=EXCLUDED.is_active,
            last_seen=NOW()
        RETURNING *
        """
        return await self.execute(sql, full_name, telegram_id, username, type, fetchrow=True)

    async def add_json_file_user(self, full_name, username, phone, telegram_id, score):
        sql = "INSERT INTO users (full_name, username, phone, telegram_id, score) VALUES($1, $2, $3,$4,$5) returning *"
        return await self.execute(sql, full_name, username, phone, telegram_id, score, fetchrow=True)

    async def select_all_users(self):
        sql = "SELECT * FROM Users"
        return await self.execute(sql, fetch=True)

    async def select_user(self, **kwargs):
        sql = "SELECT * FROM Users WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def select_top_users(self, lim_win):
        sql = f"SELECT * FROM Users WHERE score IS NOT NULL ORDER BY score DESC LIMIT {lim_win}"
        return await self.execute(sql, fetch=True)

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM Users"
        return await self.execute(sql, fetchval=True)

    async def count_active_users(self):
        sql = "SELECT COUNT(is_active) FROM Users WHERE is_active=1"
        return await self.execute(sql, fetchval=True)
    async def count_block_users(self):
        sql = "SELECT COUNT(is_active) FROM Users WHERE is_active=0"
        return await self.execute(sql, fetchval=True)

    async def add_admin(self, telegram_id: int):
        sql = "INSERT INTO Admins (telegram_id) VALUES($1) ON CONFLICT (telegram_id) DO NOTHING RETURNING telegram_id"
        return await self.execute(sql, telegram_id, fetchrow=True)

    async def remove_admin(self, telegram_id: int):
        sql = "DELETE FROM Admins WHERE telegram_id=$1 RETURNING telegram_id"
        return await self.execute(sql, telegram_id, fetchrow=True)

    async def is_admin(self, telegram_id: int) -> bool:
        sql = "SELECT EXISTS(SELECT 1 FROM Admins WHERE telegram_id=$1)"
        return bool(await self.execute(sql, telegram_id, fetchval=True))

    async def select_admins(self):
        sql = "SELECT telegram_id FROM Admins ORDER BY added_at, telegram_id"
        return await self.execute(sql, fetch=True)

    async def update_users_from_lang(self, from_lang, to_lang, tg_id):
        sql = "UPDATE Users SET from_lang=$1, to_lang=$2 where telegram_id=$3"
        return await self.execute(sql, from_lang, to_lang, tg_id, execute=True)

    async def update_users_type(self, type, tg_id):
        sql = "UPDATE Users SET is_active=$1 where telegram_id=$2"
        return await self.execute(sql, type, tg_id, execute=True)

    async def delete_users(self, telegram_id):
        sql = "DELETE FROM Users WHERE telegram_id=$1"
        await self.execute(sql, telegram_id, execute=True)

    async def drop_users(self):
        await self.execute("DROP TABLE Users", execute=True)

    async def delete_channel(self, chanel):
        sql = "DELETE FROM Channel WHERE chanelll=$1"
        await self.execute(sql, chanel, execute=True)

    async def select_chanel(self):
        sql = "SELECT * FROM Channel"
        return await self.execute(sql, fetch=True)
    async def get_chanel(self, channel):
        sql = f"SELECT * FROM Channel WHERE chanelll=$1"
        return await self.execute(sql, channel, fetch=True)

    async def add_chanell(self, chanelll, url):
        sql = "INSERT INTO Channel (chanelll, url) VALUES($1, $2) returning *"
        return await self.execute(sql, chanelll, url, fetchrow=True)

    async def get_from(self, tg_id):
        sql = f"SELECT from_lang, to_lang FROM Users WHERE telegram_id=$1"
        return await self.execute(sql, tg_id, fetch=True)

    async def drop_Chanel(self):
        await self.execute("DROP TABLE Channel", execute=True)

    async def delete_channel(self, chanel):
        sql = "DELETE FROM Channel WHERE chanelll=$1"
        await self.execute(sql, chanel, execute=True)

    async def select_chanel(self):
        sql = "SELECT * FROM Channel"
        return await self.execute(sql, fetch=True)
