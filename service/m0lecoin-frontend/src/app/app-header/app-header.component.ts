import { Component, OnInit } from '@angular/core';
import { Router, RouterStateSnapshot } from '@angular/router';
import { AuthService } from '../services';

@Component({
  selector: 'app-header',
  templateUrl: './app-header.component.html',
  styleUrls: ['./app-header.component.scss']
})
export class AppHeaderComponent implements OnInit {

  constructor(
    private router: Router,
    private auth: AuthService
  ) { }

  ngOnInit(): void {
  }

  logged() {
    return this.auth.isLogged();
  }

  handleLogButton() {
    if (this.logged()) {
      this.auth.logout();
      this.navigateTo('');
    } else {
      this.router.navigate(['login'], { queryParams: { returnUrl: this.router.url }});
    }
  }

  isLoginPage() {
    return this.router.url.startsWith('/login');
  }
  
  navigateTo(dest: string) {
    this.router.navigate([`/${dest}`]);
  }
}
