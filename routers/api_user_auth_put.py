from fastapi import APIRouter, Request, Form
from fastapi.responses import JSONResponse
import mysql.connector
from utils.token_verify_creator import token_creator
from utils.datamodel import SignInDataModel
from pydantic import ValidationError


router = APIRouter()
headers = {"Content-Type": "application/json; charset=utf-8"}

@router.put("/api/user/auth")
async def api_user_put(request: Request, login_data: SignInDataModel): # ,email: str = Form(...), password: str= Form(...)
    try:
        db_pool = request.state.db_pool.get("basic_db") 
        with db_pool.get_connection() as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM user_info WHERE email = %s AND password = %s;", (login_data.email,login_data.password,)) 
                data = cursor.fetchone()

                if data:
                    input_data = {"id": data['id'],'username':data['username'],'email':data['email'], 'password':data['password']}                                        
                    access_token = token_creator(data=input_data)                  
                    return JSONResponse(status_code=200,content={"access_token": access_token, "token_type": "bearer"}, headers=headers)
                return JSONResponse(status_code=400,content={"error": True, "message": 'Invalid user info, please make sure the email and password are correct.'}, headers=headers)

    except (mysql.connector.Error) as err:
        return JSONResponse(
            status_code=500,
            content={"error": True, "message": str(err)},
            headers=headers
        )
    except ValidationError as err:
        return JSONResponse(
            status_code=422,
            content={"error": True, "message": err.errors()}, # .errors()可以返回更仔細的資料
            headers=headers
        )     
    except (ValueError, Exception) as err:
        return JSONResponse(
            status_code=400,
            content={"error": True, "message": str(err)},
            headers=headers
        )