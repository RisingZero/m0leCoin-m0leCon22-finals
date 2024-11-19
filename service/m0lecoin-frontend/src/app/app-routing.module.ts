import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { AuthGuardService } from './services';

import { BankComponent } from './bank/bank.component';
import { ShopComponent } from './shop/shop.component';
import { WalletComponent } from './wallet/wallet.component';
import { LoginComponent } from './login/login.component';

const routes: Routes = [
  {
    path: '',
    redirectTo: 'wallet',
    pathMatch: 'full'
  },
  {
    path: 'home',
    redirectTo: 'wallet',
    pathMatch: 'full'
  },
  {
    path: 'login',
    component: LoginComponent
  },
  {
    path: 'wallet',
    component: WalletComponent
  },
  {
    path: 'bank',
    component: BankComponent,
    canActivate:[AuthGuardService]
  },
  {
    path: 'shop',
    component: ShopComponent,
    canActivate:[AuthGuardService]
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
