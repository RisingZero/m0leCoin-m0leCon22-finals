import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, throwError, Subject, Subscription, lastValueFrom  } from 'rxjs';
import { catchError, retry } from 'rxjs/operators';

import { environment } from 'src/environments/environment';

import {
  LoginRequest,
  LoginResponse,
  RegisterRequest
} from 'src/app/models';

import { MessageService } from 'primeng/api';
import { Web3Service } from './web3.service';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private userAddress: string | null;
  private logged = false;
  private web3Linked = false

  private loginEventSource = new Subject<boolean>();
  loginEvent = this.loginEventSource.asObservable();

  web3subscription: Subscription;

  constructor(
    private http: HttpClient,
    private web3Service: Web3Service,
    private messageService: MessageService
  ) {
    this.web3subscription = this.web3Service.linkStatus.subscribe(
      (linked) => {
        console.log(linked);
        this.web3Linked = linked;
        if (!linked) {
          this.logged = false;
        }
      }
    )
    this.userAddress = '';
    if (this.web3Linked && localStorage.getItem('jwt_token') && localStorage.getItem('user_address')) {
      this.logged = true;
      this.loginEventSource.next(true);
      this.userAddress = localStorage.getItem('user_address');
    }
  }

  async register(address: string, password: string) {
    if (!address || !password) {
      return;
    }
    const otpRequest = this.http.get<{otp: string}>(`${environment.baseUrl}/otp`, {
      params: {
        "address": address
      }
    });
    const otp = (await lastValueFrom(otpRequest)).otp;
    const otpSign = await this.web3Service.sign(otp, address);
    if (otpSign !== '') {
      const body: RegisterRequest = {
        address, password, otp, otpSign
      };
      this.http.post<LoginResponse>(`${environment.baseUrl}/register`, body).subscribe(
        (data) => {
          if (data.success) {
            this.logged = true;
            this.userAddress = address;
            localStorage.setItem('jwt_token', data.token);
            localStorage.setItem('user_address', address);
            this.messageService.add({severity: 'success', summary: 'Registration successful.'});
            this.loginEventSource.next(true);
            if (this.web3Service.web3) {
              this.web3Service.web3.eth.defaultAccount = this.userAddress;
            }
          } else {
            this.messageService.add({severity: 'error', summary: 'Registration failed.', detail: data.message});
          }
        },
        (err) => {
          this.messageService.add({severity: 'error', summary: 'Registration failed.', detail: err});
        }  
      );  
    }
  }

  login(address: string, password: string) {
    const body: LoginRequest = {
      address, password
    };
    this.http.post<LoginResponse>(`${environment.baseUrl}/login`, body).subscribe(
      (data) => {
        if (data.success) {
          this.logged = true;
          this.userAddress = address;
          localStorage.setItem('jwt_token', data.token);
          localStorage.setItem('user_address', address);
          this.messageService.add({severity: 'success', summary: 'Login successful.'});
          this.loginEventSource.next(true);
          if (this.web3Service.web3) {
            this.web3Service.web3.eth.defaultAccount = this.userAddress;
          }
        } else {
          this.messageService.add({severity: 'error', summary: 'Login failed.', detail: data.message});
        }
      },
      (err) => {
        this.messageService.add({severity: 'error', summary: 'Login failed.', detail: err});
      }
    );
  }

  isLogged(): boolean {
    return this.logged;
  }

  isweb3Linked(): boolean{
    return this.web3Linked;
  }

  getUserAddress(): string {
    if (this.userAddress) {
      return this.userAddress;
    }
    return '';
  }

  getToken() {
    return localStorage.getItem('jwt_token');
  }

  logout() {
    this.logged = false;
    this.userAddress = '';
    localStorage.removeItem('jwt_token');
    localStorage.removeItem('user_address');
    this.loginEventSource.next(false);
  }
}
