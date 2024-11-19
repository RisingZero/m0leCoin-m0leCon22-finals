/* 
 *  API RESPONSE MODEL OBJECTS
 *
 */

export interface GenericResponse {
    success: boolean,
    message: string
}
export interface LoginResponse extends GenericResponse {
    token: string
}

export interface Product {
    id: number,
    title: string,
    content: string,
    seller: string,
    price: number
}

export interface Gadget {
    id: number,
    content: string,
    seller: string
}
