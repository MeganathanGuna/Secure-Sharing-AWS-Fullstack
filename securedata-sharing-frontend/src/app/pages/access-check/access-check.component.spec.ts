import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AccessCheckComponent } from './access-check.component';

describe('AccessCheckComponent', () => {
  let component: AccessCheckComponent;
  let fixture: ComponentFixture<AccessCheckComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AccessCheckComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AccessCheckComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
