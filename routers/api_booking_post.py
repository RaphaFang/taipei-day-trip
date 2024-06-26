from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from utils.token_verify_creator import token_verifier
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from utils.datamodel import BookingDataMode
import mysql.connector

router = APIRouter()
headers = {"Content-Type": "application/json; charset=utf-8"}
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/api/booking")   
async def api_booking_post(request: Request, token: str = Depends(oauth2_scheme)):
    # 如果資料放在 header ，ValidationError 的驗證會搶在所有api運作邏輯之前執行，解決方式是把資料放在body，不放在header
    # 原先放在header，還是要注意 data 要在 token 前面，因為 token有默認值，前者沒有...
    try:
        if token == 'null':
            content_data = {"error": True, "message": "Please log-in to access the booking page."}
            return JSONResponse(status_code=403,content=content_data, headers=headers)
        input_token = token_verifier(token)
        if input_token:
            body = await request.json()
            data = BookingDataMode(**body)

        if data:
            db_pool = request.state.db_pool.get("basic_db") 
            with db_pool.get_connection() as connection:
                with connection.cursor(dictionary=True) as cursor:
                    cursor.execute("""
                        INSERT INTO user_booking_tentative (
                            creator_id, attraction_id, name, address, image, date, time, price
                        )
                        SELECT %s, id, name, address, JSON_UNQUOTE(JSON_EXTRACT(images, '$[0]')), %s, %s, %s
                        FROM processed_data
                        WHERE id = %s
                        ON DUPLICATE KEY UPDATE
                            attraction_id = VALUES(attraction_id),
                            name = VALUES(name),
                            address = VALUES(address),
                            image = VALUES(image),
                            date = VALUES(date),
                            time = VALUES(time),
                            price = VALUES(price);
                    """, (
                        input_token['id'],  
                        body['date'],     
                        body['time'],       
                        body['price'],    
                        body['attractionId'] 
                    ))
                    
                    connection.commit()
                    content_data={"ok": True}
                    return JSONResponse(status_code=200,content=content_data, headers=headers)

    except (mysql.connector.Error) as err:
        return JSONResponse(
            status_code=500,
            content={"error": True, "message": str(err)},
            headers=headers
        )
    except (ValueError,Exception) as err:
        return JSONResponse(
            status_code=400,
            content={"error": True, "message": str(err)},
            headers=headers
        )
