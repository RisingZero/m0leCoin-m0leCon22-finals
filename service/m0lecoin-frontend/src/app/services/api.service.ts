import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { lastValueFrom, timeout } from 'rxjs';
import { environment } from 'src/environments/environment';
import { Gadget, GenericResponse, Product } from '../models';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class ApiService {

  constructor(
    private http: HttpClient,
    private auth: AuthService
  ) { }

  async getShopProducts() {
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${this.auth.getToken()}`
    })
    const res = await lastValueFrom(
      this.http.get<Product[]>(`${environment.baseUrl}/digitalproducts`, {
        headers: headers
      }
      ).pipe(timeout(5000))
    );
    return res;
  }

  async getShopProductContent(productId: number) {
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${this.auth.getToken()}`
    })
    const res = await lastValueFrom(
      this.http.get<Product>(`${environment.baseUrl}/digitalproducts/${productId}`, {
        headers: headers
      }
      ).pipe(timeout(5000))
    );
    return res;
  }

  async sellShopProduct(product: Product) {
      const headers = new HttpHeaders({
        'Authorization': `Bearer ${this.auth.getToken()}`
      })
      const res = await lastValueFrom(
        this.http.post<Product>(`${environment.baseUrl}/digitalproducts`, product, {
          headers: headers
        }
        ).pipe(timeout(5000))
      );
      return res;
  }

  async revertSellShopProduct(productId: number) {
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${this.auth.getToken()}`
    })
    const res = await lastValueFrom(
      this.http.delete<GenericResponse>(`${environment.baseUrl}/digitalproducts/${productId}`, {
        headers: headers
      }
      ).pipe(timeout(5000))
    );
    return res;
  }

  async getGadgets() {
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${this.auth.getToken()}`
    })
    const res = await lastValueFrom(
      this.http.get<Gadget[]>(`${environment.baseUrl}/materialproducts`, {
        headers: headers
      }
      ).pipe(timeout(5000))
    );
    return res;
  }

  async publishGadget(gadget: Gadget) {
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${this.auth.getToken()}`
    })
    const res = await lastValueFrom(
      this.http.post<Gadget>(`${environment.baseUrl}/materialproducts`, gadget, {
        headers: headers
      }
      ).pipe(timeout(5000))
    );
    return res;
  }

  async sendGadgetToMailbox(mailbox_dest: string, hmac: string, gadgetId: number) {
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${this.auth.getToken()}`
    })
    const res = await lastValueFrom(
      this.http.post<GenericResponse>(`${environment.baseUrl}/materialproducts/${gadgetId}`, {
        destination: mailbox_dest,
        hmac: hmac
      }, {
        headers: headers
      }
      ).pipe(timeout(5000))
    );
    return res;
  }

  async updateGagdetKey(key: string) {
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${this.auth.getToken()}`
    })
    const res = await lastValueFrom(
      this.http.post<GenericResponse>(`${environment.baseUrl}/set-gadget-key`, {
        key: key
      }, {
        headers: headers
      }
      ).pipe(timeout(5000))
    );
    return res;
  }

  async deleteGadget(gadgetId: number) {
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${this.auth.getToken()}`
    })
    const res = await lastValueFrom(
      this.http.delete<GenericResponse>(`${environment.baseUrl}/materialproducts/${gadgetId}`, {
        headers: headers
      }
      ).pipe(timeout(5000))
    );
    return res;
  }
}
