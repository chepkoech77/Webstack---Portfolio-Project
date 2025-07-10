from fastapi import FastAPI, HTTPException, Request, status, Depends
from fastapi.responses import HTMLResponse
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator
from models import User, GC, Product
from tortoise.exceptions import IntegrityError
from typing import List, Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from auth import *

# Models
User_Pydantic = pydantic_model_creator(User, name="User", exclude=("is_verified",))
UserIn_Pydantic = pydantic_model_creator(User, name="UserIn", exclude_readonly=True)
UserOut_Pydantic = pydantic_model_creator(User, name="UserOut", exclude=("password",))
GC_Pydantic = pydantic_model_creator(GC, name="GC")
GCIn_Pydantic = pydantic_model_creator(GC, name="GCIn", exclude_readonly=True)
Product_Pydantic = pydantic_model_creator(Product, name="Product")
ProductIn_Pydantic = pydantic_model_creator(Product, name="ProductIn", exclude_readonly=True)

# App
app = FastAPI(
    title="GCAPI",
    version="0.1.1",
    description="E-con API built with FastAPI and JWT"
)

oauth_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Token
@app.post("/token", tags=["User"])
async def generate_token(request_form: OAuth2PasswordRequestForm = Depends()):
    token = await token_generator(request_form.username, request_form.password)
    return {"access_token": token, "token_type": "bearer"}

# Auth user
async def get_current_user(token: str = Depends(oauth_scheme)):
    return await verify_token(token)

# User info
@app.post("/users/me", tags=["User"])
async def client_data(user: UserIn_Pydantic = Depends(get_current_user)):
    return {
        "status": "ok",
        "data": {
            "username": user.username,
            "email": user.email,
            "is_verified": user.is_verified,
            "join_date": user.join_date.strftime("%b %d %Y")
        }
    }

# All users
@app.get("/users/", tags=["User"], response_model=List[UserOut_Pydantic])
async def get_users(skip: int = 0, limit: int = 10, user: UserIn_Pydantic = Depends(get_current_user)):
    return await User.filter(id__gt=skip, id__lte=skip + limit)

# Register user
@app.post("/users/", tags=["User"], status_code=status.HTTP_201_CREATED, response_model=UserOut_Pydantic)
async def user_registration(user: UserIn_Pydantic):
    info = user.dict(exclude_unset=True)
    if len(info["password"]) < 8:
        raise HTTPException(status_code=400, detail="Password too short")
    if len(info["username"]) < 5:
        raise HTTPException(status_code=400, detail="Username too short")
    if await User.exists(username=info["username"]):
        raise HTTPException(status_code=400, detail="Username exists")
    if await User.exists(email=info["email"]):
        raise HTTPException(status_code=400, detail="Email exists")
    info["password"] = get_hashed_password(info["password"])
    try:
        obj = await User.create(**info)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Create failed")
    return await UserOut_Pydantic.from_tortoise_orm(obj)

# One user
@app.get("/users/{user_id}", tags=["User"], response_model=UserOut_Pydantic)
async def read_user(user_id: int):
    user = await UserOut_Pydantic.from_queryset_single(User.get(id=user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Update user
@app.put("/users/{user_id}", tags=["User"], response_model=UserOut_Pydantic)
async def update_user(user_id: int, user: UserIn_Pydantic):
    await User.filter(id=user_id).update(**user.dict(exclude_unset=True))
    return await UserOut_Pydantic.from_queryset_single(User.get(id=user_id))

# Delete user
@app.delete("/users/{user_id}", tags=["User"], status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    deleted = await User.filter(id=user_id).delete()
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return None

# Add GC
@app.post("/gcs/", tags=["GC"], status_code=status.HTTP_201_CREATED, response_model=GC_Pydantic)
async def create_gc(gc: GCIn_Pydantic, user: User = Depends(get_current_user)):
    info = gc.dict(exclude_unset=True)
    info["owner_id"] = user.id
    obj = await GC.create(**info)
    return await GC_Pydantic.from_tortoise_orm(obj)

# All GCs
@app.get("/gcs/", tags=["GC"], response_model=List[GC_Pydantic])
async def read_gcs(skip: int = 0, limit: int = 10):
    return await GC_Pydantic.from_queryset(GC.all().offset(skip).limit(limit))

# One GC
@app.get("/gcs/{gc_id}", tags=["GC"], response_model=GC_Pydantic)
async def read_gc(gc_id: int):
    gc = await GC_Pydantic.from_queryset_single(GC.get(id=gc_id))
    if not gc:
        raise HTTPException(status_code=404, detail="GC not found")
    return gc

# Update GC
@app.put("/gcs/{gc_id}", tags=["GC"], response_model=GC_Pydantic)
async def update_gc(gc_id: int, gc: GCIn_Pydantic):
    await GC.filter(id=gc_id).update(**gc.dict(exclude_unset=True))
    return await GC_Pydantic.from_queryset_single(GC.get(id=gc_id))

# Delete GC
@app.delete("/gcs/{gc_id}", tags=["GC"], status_code=status.HTTP_204_NO_CONTENT)
async def delete_gc(gc_id: int):
    deleted = await GC.filter(id=gc_id).delete()
    if not deleted:
        raise HTTPException(status_code=404, detail="GC not found")
    return None

# Add product
@app.post("/products/", tags=["Product"], status_code=status.HTTP_201_CREATED, response_model=Product_Pydantic)
async def create_product(product: ProductIn_Pydantic):
    obj = await Product.create(**product.dict(exclude_unset=True))
    return await Product_Pydantic.from_tortoise_orm(obj)

# All products
@app.get("/products/", tags=["Product"], response_model=List[Product_Pydantic])
async def read_products(skip: int = 0, limit: int = 10):
    return await Product_Pydantic.from_queryset(Product.all().offset(skip).limit(limit))

# One product
@app.get("/products/{product_id}", tags=["Product"], response_model=Product_Pydantic)
async def read_product(product_id: int):
    product = await Product_Pydantic.from_queryset_single(Product.get(id=product_id))
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Update product
@app.put("/products/{product_id}", tags=["Product"], response_model=Product_Pydantic)
async def update_product(product_id: int, product: ProductIn_Pydantic):
    await Product.filter(id=product_id).update(**product.dict(exclude_unset=True))
    return await Product_Pydantic.from_queryset_single(Product.get(id=product_id))

# Delete product
@app.delete("/products/{product_id}", tags=["Product"], status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int):
    deleted = await Product.filter(id=product_id).delete()
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    return None

# DB config
register_tortoise(
    app,
    db_url="sqlite://db.sqlite3",
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

