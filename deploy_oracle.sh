cd m0lecoin-otp-oracle-mailbox

docker-compose --env-file .env up -d --build

## ORACLE API AT 0.0.0.0:10000

# ENDPOINT OTP: GET /signature
# ENPOINTS MAILBOX
#   - GET   /mailbox/<box>
#   - POST  /mailbox/<box>  (body data)
