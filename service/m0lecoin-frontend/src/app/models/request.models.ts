export interface LoginRequest {
    address: string,
    password: string
}

export interface RegisterRequest extends LoginRequest {
    otp: string,
    otpSign: string
}
