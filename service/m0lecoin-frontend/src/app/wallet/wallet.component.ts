import { Component, OnInit } from '@angular/core';
import { Subscription } from 'rxjs';
import { AuthService, Web3Service } from '../services';

@Component({
  selector: 'app-wallet',
  templateUrl: './wallet.component.html',
  styleUrls: ['./wallet.component.scss']
})
export class WalletComponent implements OnInit {
  
  loginEventSubscription: Subscription;
  logged = false;
  
  userAddress = '';
  tokenBalance = 0;
  transferDestinationAddress = '';
  transferQuantity = 0;

  constructor(
    private auth: AuthService,
    private web3Service: Web3Service
  ) {
    this.userAddress = this.auth.getUserAddress();
    this.loginEventSubscription = this.auth.loginEvent.subscribe(logged => {
      this.logged = logged;
    });
  }

  ngOnInit(): void {
    this.logged = this.auth.isLogged();
    if (this.logged) {
      this.checkBalance();
    }
  }

  checkBalance() {
    this.web3Service.getUserBalance()
      .then(b => this.tokenBalance = b);
  }

  transfer() {
    this.web3Service.transferTokens(this.transferDestinationAddress, this.transferQuantity)
      .then(() => this.checkBalance());
  }
}
