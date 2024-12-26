from typing import Annotated, List
from pydantic import BaseModel


from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles

from contextlib import asynccontextmanager
from sqlmodel import Field, Session, SQLModel, create_engine, select

import os


class IPAddress(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    ip: str = Field(index=True)
    hostname: str | None = Field(default=None, index=True)
    purpose: str | None = Field(default=None, index=True)
    device_type: str | None = Field(default=None, index=True)
    admin: str | None = Field(default=None, index=True)
    status: bool | None = Field(default=None, index=True)


class Message(BaseModel):
    message: str
    data: List[IPAddress]


class Admin(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str | None = Field(default=None, index=True)
    grade: str | None = Field(default=None, index=True)


class AliveServers(BaseModel):
    ping: List[str]


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


def update_ip(ip: IPAddress, ip_update: IPAddress):
    ip.ip = ip_update.ip
    ip.hostname = ip_update.hostname
    ip.purpose = ip_update.purpose
    ip.device_type = ip_update.device_type
    ip.admin = ip_update.admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

# SQLiteデータベースの設定
basedir = os.path.abspath(os.path.dirname(__file__))
sqlite_url = "sqlite:///" + os.path.join(basedir, "ip_management.db")
engine = create_engine(sqlite_url)

SessionDep = Annotated[Session, Depends(get_session)]


@app.post("/api/ip-addresses", response_model=IPAddress)
def create_ip_address(ip: IPAddress, session: SessionDep):
    statement = select(IPAddress).where(IPAddress.ip == ip.ip)
    ip_exist = session.exec(statement).all()
    if ip_exist:
        raise HTTPException(status_code=409, detail="the ip_address already registered")

    session.add(ip)
    session.commit()
    session.refresh(ip)
    return ip


@app.put("/api/ip-addresses", response_model=IPAddress)
def change_ip_address(ip: IPAddress, session: SessionDep):
    statement = select(IPAddress).where(IPAddress.ip == ip.ip)
    ip_exist = session.exec(statement).all()
    if not ip_exist:
        raise HTTPException(status_code=404, detail="ip_address not found")
    update_ip(ip_exist[0], ip)
    session.add(ip)
    session.commit()
    session.refresh(ip)
    return ip


@app.get("/api/ip-addresses", response_model=List[IPAddress])
def get_ip_addresses(session: SessionDep):
    ip_addresses = session.exec(select(IPAddress)).all()
    return ip_addresses


@app.delete("/api/ip-addresses")
def delete_ip_address(ip: IPAddress, session: SessionDep):
    ip = session.get(IPAddress, ip.id)
    if ip is None:
        raise HTTPException(status_code=404, detail="ip_address not found")
    session.delete(ip)
    session.commit()
    return {"message": "IP address deleted successfully"}


@app.get("/api/admins", response_model=List[Admin])
def get_admins(session: SessionDep):
    admins = session.exec(select(Admin)).all()
    return admins


@app.post("/api/zabbix", response_model=Message)
def updateState(alive_servers: AliveServers, session: SessionDep):
    ip_addresses = session.exec(select(IPAddress)).all()
    for ip in ip_addresses:
        if ip.ip in alive_servers.ping:
            ip.status = True
            alive_servers.ping.remove(ip.ip)
        else:
            ip.status = False

    for alive_server in alive_servers.ping:
        ip = IPAddress(ip=alive_server, status=True)
        session.add(ip)
    session.commit()
    return Message(message="Machine state changed successfully", data=ip_addresses)


app.mount("/", StaticFiles(directory="../dist", html=True), name="static")
