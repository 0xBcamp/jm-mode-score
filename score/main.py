from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from routers import covalent, kyc

#from routers import Covalent
#from routers import plaid

from support.database import engine
from support import models


models.Base.metadata.create_all(bind=engine)
app = FastAPI()


# throttle control
limiter = Limiter(key_func=get_remote_address, default_limits=['5/minute'])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)


# validator routers
#app.include_router(coinbase.router)
#app.include_router(plaid.router)


app.include_router(covalent.router)



# kyc router - validator agnostic
app.include_router(kyc.router)


# error handling
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({'error': exc.errors()})
    )
