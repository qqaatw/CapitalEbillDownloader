import re
import requests
import typing

from PIL import Image
from io import BytesIO
from pydantic import BaseModel, Field

from sign_ca import sign

# Models

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    "Referer": "https://www.capital.com.tw/Service2/Member/Login/Default.asp",
    "Host": "www.capital.com.tw",
    "Origin": "https://www.capital.com.tw"
}

class CAProcessModel(BaseModel):
    GUID = ""
    selBillType = ""
    CustID: str
    B64Sig: str
    RawData = ",EBill_Login"
    CertID = ""
    CertType = ""
    Context = "EBill_Login"
    rtn = "-1"
    Browser = "CHROME"

class LoginModel(BaseModel):
    MsgID = "NoLogin"
    GoToURL = "/Service2/account/membill/ebillDefault.asp"
    CustID: str
    Password: str
    loginValidCode1: str
    imageField32x_field: int = Field(12, alias='imageField32.x')
    imageField32y_field: int = Field(8, alias='imageField32.y')


class DailyEBillModel(BaseModel):
    GUID: typing.Optional[str] = ""
    selBillType = ""
    billType2 = "1"
    ShowType = "1"
    data_YM: typing.Optional[str] = ""


class MonthEBillModel(BaseModel):
    GUID: typing.Optional[str] = ""
    selBillType = ""
    billType2 = "0"
    ShowType = "0"
    group1 = "HTML"
    data_YM: typing.Optional[str] = ""

class DailyEbillRefreshModel(BaseModel):
    data_YM: str
    ShowType = "1"

class MonthEbillRefreshModel(BaseModel):
    data_YM: str
    ShowType = "0"

# Functions

def login(s, national_id, password):
    # Get VerifyProcess Cookie first
    r = s.get('https://www.capital.com.tw/Service2/Member/Login/Default.asp')

    input_code = ""
    while len(input_code) != 4:
        # Validation code.
        r = s.get(
            'https://www.capital.com.tw/Service2/Member/Login/asp/aspjpeg2.asp',
            cookies=s.cookies
        )
        # Show code and provide input
        code_img = Image.open(BytesIO(r.content))
        code_img.show()

        input_code = input("請輸入驗證碼 Please enter validation code:")

    login = LoginModel(
        CustID=national_id,
        Password=password,
        loginValidCode1=input_code)

    r = s.request(
        method='post',
        url='https://www.capital.com.tw/Service2/Member/Login/Login_Proc.asp',
        data=login.dict(by_alias=True),
        cookies=s.cookies
    )
    r.encoding = 'big5'
    
    return r.ok, r

def load_ebill_available_dates(s):
    ebill_model = DailyEBillModel()
    r = s.request(
        method='post',
        url='https://www.capital.com.tw/Service2/account/membill/ebillDefault.asp',
        data=ebill_model.dict(by_alias=True),
        cookies=s.cookies
    )
    r.encoding = 'big5'

    return r.ok, r

def load_ebill_by_date(s, date):
    ebill_refresh_model = DailyEbillRefreshModel(data_YM=date)
    r = s.request(
        method='get',
        url='https://www.capital.com.tw/Service2/account/membill/ref.asp',
        data=ebill_refresh_model.dict(by_alias=True),
        cookies=s.cookies
    )
    r.encoding = 'big5'

    GUID = re.search(r"\{.{8}-.{4}-.{4}-.{4}-.{12}\}", r.text)[0]

    ebill_model = DailyEBillModel(data_YM=date, GUID=GUID)
    r = s.request(
        method='post',
        url='https://www.capital.com.tw/Service2/account/membill/ebillDefault.asp',
        data=ebill_model.dict(by_alias=True),
        cookies=s.cookies
    )
    r.encoding = 'big5'

    return r.ok, r

def load_ebill_by_month(s, month):
    ebill_refresh_model = MonthEbillRefreshModel(data_YM=month)
    r = s.request(
        method='get',
        url='https://www.capital.com.tw/Service2/account/membill/ref.asp',
        data=ebill_refresh_model.dict(by_alias=True),
        cookies=s.cookies
    )
    r.encoding = 'big5'

    GUID = re.search(r"\{.{8}-.{4}-.{4}-.{4}-.{12}\}", r.text)[0]

    ebill_model = MonthEBillModel(data_YM=month, GUID=GUID)
    r = s.request(
        method='post',
        url='https://www.capital.com.tw/Service2/account/membill/ebillDefault.asp',
        data=ebill_model.dict(by_alias=True),
        cookies=s.cookies
    )
    r.encoding = 'big5'

    return r.ok, r

def verify_CA(s, national_id, p12_b64_cert):
    verified, signed_data = sign(p12_b64_cert, national_id, ",EBill_Login")
    
    if not verified:
        raise RuntimeError('The signed certificate cannnot be verified.')

    # Actually, the server doesn't verify B64Sig.
    # Even if a blank string is provided, the verifying process still passes.
    ca_process_model = CAProcessModel(CustID=national_id, B64Sig=signed_data)
    r = s.request(
        method='post',
        url='https://www.capital.com.tw/Service2/account/membill/Check_Proc2.asp',
        data=ca_process_model.dict(by_alias=True),
        cookies=s.cookies
    )

    return r.ok, r