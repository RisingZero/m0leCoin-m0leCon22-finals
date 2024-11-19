import { Component, OnInit } from '@angular/core';
import { AuthService, Web3Service } from '../services';
import { Router, ActivatedRoute } from '@angular/router';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {

  accounts: any[] = [];
  selectedAccount: any;
  password = '';
  
  returnUrl: string;

  loginEventSubscription: Subscription;

  constructor(
    private auth: AuthService,
    private route: ActivatedRoute,
    private router: Router,
    private web3Service: Web3Service
  ) {
    this.returnUrl = this.route.snapshot.queryParams['returnUrl'];
    this.loginEventSubscription = this.auth.loginEvent.subscribe(logged => {
      if (logged) {
        this.router.navigateByUrl(this.returnUrl);
      }
    });
  }

  ngOnInit(): void {

  }

  register() {
    this.auth.register(this.selectedAccount, this.password);
  }

  login() {
    this.auth.login(this.selectedAccount, this.password);
  }

  async onWalletConnect() {
    this.accounts = await this.web3Service.connectAccount();
  }
}
