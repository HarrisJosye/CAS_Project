
# app/scripts/seed_demo_user.py
import asyncio
from sqlalchemy import select
from passlib.context import CryptContext
from app.db.base import init_db, get_session
from app.db.repositories import UserRepository

pwd = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

async def main():
    await init_db()
    async with get_session() as session:
        repo = UserRepository(session)
        user = await repo.get_by_username("demo")
        if user:
            user.hashed_password = pwd.hash("demo123!")
            print("Updated demo user's password hash")
        else:
            hashed = pwd.hash("demo123!")
            await repo.insert(sub="user:demo", username="demo", hashed_password=hashed)
            print("Inserted demo user")
        await session.commit()

if __name__ == "__main__":
    asyncio.run(main())


"""
docker compose down
docker compose build --no-cache api
docker compose up -d
docker compose exec api python -m app.scripts.seed_demo_user


docker-compose.yml
environment:
  - JWT_SECRET=${JWT_SECRET}
  - JWT_ISSUER=${JWT_ISSUER}
  - JWT_AUDIENCE=${JWT_AUDIENCE}
  - JWT_EXPIRE_MIN=${JWT_EXPIRE_MIN}

  

"""