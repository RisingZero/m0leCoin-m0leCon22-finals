import { Component, OnInit } from '@angular/core';
import { Web3Service } from '../services';

import { MessageService } from 'primeng/api';

@Component({
  selector: 'app-bank',
  templateUrl: './bank.component.html',
  styleUrls: ['./bank.component.scss']
})
export class BankComponent implements OnInit {

  registered = false;

  balance = 0;
  depositValue = 0;

  bankOtpHash = '';
  bankOtpV = '';
  bankOtpR = '';
  bankOtpS = '';

  constructor(
    private web3Service: Web3Service,
    private messageService: MessageService
  ) {
  }

  ngOnInit(): void {
    this.checkBankRegistration();
  }

  checkBankRegistration() {
    this.web3Service.checkBankRegistration()
    .then(res => {
      this.registered = res;
      if (res) {
        this.checkBankBalance();
      }
    });
  }

  openBankAccount() {
    if (this.bankOtpHash === '' || this.bankOtpV === '' || this.bankOtpR === '' || this.bankOtpS === '') {
      this.messageService.add({severity: 'error', summary: 'Please fill in the otp signature data!'});
      return;
    }

    this.web3Service.openBankAccount(this.bankOtpHash, parseInt(this.bankOtpV), this.bankOtpR, this.bankOtpS)
      .then(() => this.checkBankRegistration());
  }

  checkBankBalance() {
    if (this.registered) {
      this.web3Service.getUserBankBalance()
      .then(b => this.balance = b);
    }
  }

  async deposit() {
    const realBalance = await this.web3Service.getUserBalance();
    if (realBalance < this.depositValue) {
      this.messageService.add({severity: 'error', summary: 'Insufficient balance!'});
      return;
    }
    this.web3Service.bankDeposit(this.depositValue)
      .then(() => this.checkBankBalance());
  }

  withdraw() {
    this.web3Service.bankWithdraw()
      .then(() => this.checkBankBalance());
  }

}
