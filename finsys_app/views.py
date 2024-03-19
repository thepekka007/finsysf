#Finsys Final
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render,redirect
from django.contrib.auth.models import User, auth
from . models import *
# from Finsys_App.models import Fin_Vendors

from django.contrib import messages
from django.utils.crypto import get_random_string
from datetime import date
from datetime import timedelta
import random
import string
import io
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.core.mail import send_mail, EmailMessage
from io import BytesIO
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import datetime
from datetime import date,datetime
from django.db.models import Sum,F,IntegerField,Q
from django.db.models.functions import ExtractMonth,ExtractYear,Cast
from django.core.mail import EmailMessage
from django.urls import reverse
from django.http import HttpResponse
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.db import models
from bs4 import BeautifulSoup
from openpyxl import Workbook
from openpyxl import load_workbook
from django.http import HttpResponse,HttpResponseRedirect
from datetime import date
from django.db.models import Max
import logging
import re   
import os
from decimal import Decimal

def Fin_index(request):
    return render(request,'Fin_index.html')


def Fin_login(request):
    if request.method == 'POST':
        user_name = request.POST['username']
        passw = request.POST['password']
    
        log_user = auth.authenticate(username = user_name,
                                  password = passw)
    
        if log_user is not None:
            auth.login(request, log_user)

        # ---super admin---

            if request.user.is_staff==1:
                return redirect('Fin_Adminhome') 
            
        # -------distributor ------    
            
        if Fin_Login_Details.objects.filter(User_name = user_name,password = passw).exists():
            data =  Fin_Login_Details.objects.get(User_name = user_name,password = passw)  
            if data.User_Type == 'Distributor':
                did = Fin_Distributors_Details.objects.get(Login_Id=data.id) 
                if did.Admin_approval_status == 'Accept':
                    request.session["s_id"]=data.id
                    if 's_id' in request.session:
                        if request.session.has_key('s_id'):
                            s_id = request.session['s_id']
                            print(s_id)
                            
                            current_day=date.today() 
                            if current_day > did.End_date:
                                print("wrong")
                                   
                                return redirect('Fin_Wrong')
                            else:
                                return redirect('Fin_DHome')
                            
                    else:
                        return redirect('/')
                else:
                    messages.info(request, 'Approval is Pending..')
                    return redirect('Fin_DistributorReg')
                      
            if data.User_Type == 'Company':
                cid = Fin_Company_Details.objects.get(Login_Id=data.id) 
                if cid.Admin_approval_status == 'Accept' or cid.Distributor_approval_status == 'Accept':
                    request.session["s_id"]=data.id
                    if 's_id' in request.session:
                        if request.session.has_key('s_id'):
                            s_id = request.session['s_id']
                            print(s_id)
                            com = Fin_Company_Details.objects.get(Login_Id = s_id)
                            

                            current_day=date.today() 
                            if current_day > com.End_date:
                                print("wrong")
                                   
                                return redirect('Fin_Wrong')
                            else:
                                return redirect('Fin_Com_Home')
                    else:
                        return redirect('/')
                else:
                    messages.info(request, 'Approval is Pending..')
                    return redirect('Fin_CompanyReg')  
            if data.User_Type == 'Staff': 
                cid = Fin_Staff_Details.objects.get(Login_Id=data.id)   
                if cid.Company_approval_status == 'Accept':
                    request.session["s_id"]=data.id
                    if 's_id' in request.session:
                        if request.session.has_key('s_id'):
                            s_id = request.session['s_id']
                            print(s_id)
                            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
                            

                            current_day=date.today() 
                            if current_day > com.company_id.End_date:
                                print("wrong")
                                messages.info(request, 'Your Account Temporary blocked')
                                return redirect('Fin_StaffReg') 
                            else:
                                return redirect('Fin_Com_Home')
                    else:
                        return redirect('/')
                else:
                    messages.info(request, 'Approval is Pending..')
                    return redirect('Fin_StaffReg') 
        else:
            messages.info(request, 'Invalid Username or Password. Try Again.')
            return redirect('Fin_CompanyReg')  
    else:  
        return redirect('Fin_CompanyReg')   
  

def logout(request):
    request.session["uid"] = ""
    auth.logout(request)
    return redirect('Fin_index')  

                    


 
    
# ---------------------------start admin ------------------------------------   


def Fin_Adminhome(request):
    noti = Fin_ANotification.objects.filter(status = 'New').order_by('-id','-Noti_date')
    n = len(noti)
    context = {
        'noti':noti,
        'n':n
    }
    return render(request,'Admin/Fin_Adminhome.html',context)

def Fin_PaymentTerm(request):
    terms = Fin_Payment_Terms.objects.all()
    noti = Fin_ANotification.objects.filter(status = 'New').order_by('-id','-Noti_date')
    n = len(noti)
    return render(request,'Admin/Fin_Payment_Terms.html',{'terms':terms,'noti':noti,'n':n})

def Fin_add_payment_terms(request):
  if request.method == 'POST':
    num=int(request.POST['num'])
    select=request.POST['select']
    if select == 'Years':
      days=int(num)*365
      pt = Fin_Payment_Terms(payment_terms_number = num,payment_terms_value = select,days = days)
      pt.save()
      messages.success(request, 'Payment term is added')
      return redirect('Fin_PaymentTerm')

    else:  
      days=int(num*30)
      pt = Fin_Payment_Terms(payment_terms_number = num,payment_terms_value = select,days = days)
      pt.save()
      messages.success(request, 'Payment term is added')
      return redirect('Fin_PaymentTerm')


  return redirect('Fin_PaymentTerm')

def Fin_ADistributor(request):
    noti = Fin_ANotification.objects.filter(status = 'New').order_by('-id','-Noti_date')
    n = len(noti)
    return render(request,"Admin/Fin_ADistributor.html",{'noti':noti,'n':n})

def Fin_Distributor_Request(request):
   data = Fin_Distributors_Details.objects.filter(Admin_approval_status = "NULL")
   print(data)
   noti = Fin_ANotification.objects.filter(status = 'New').order_by('-id','-Noti_date')
   n = len(noti)
   return render(request,"Admin/Fin_Distributor_Request.html",{'data':data,'noti':noti,'n':n})

def Fin_Distributor_Req_overview(request,id):
    data = Fin_Distributors_Details.objects.get(id=id)
    noti = Fin_ANotification.objects.filter(status = 'New').order_by('-id','-Noti_date')
    n = len(noti)
    return render(request,"Admin/Fin_Distributor_Req_overview.html",{'data':data,'noti':noti,'n':n})

def Fin_DReq_Accept(request,id):
   data = Fin_Distributors_Details.objects.get(id=id)
   data.Admin_approval_status = 'Accept'
   data.save()
   return redirect('Fin_Distributor_Request')

def Fin_DReq_Reject(request,id):
   data = Fin_Distributors_Details.objects.get(id=id)
   data.Login_Id.delete()
   data.delete()
   return redirect('Fin_Distributor_Request')

def Fin_Distributor_delete(request,id):
   data = Fin_Distributors_Details.objects.get(id=id)
   data.Login_Id.delete()
   data.delete()
   return redirect('Fin_All_distributors')

def Fin_All_distributors(request):
   data = Fin_Distributors_Details.objects.filter(Admin_approval_status = "Accept")
   print(data)
   noti = Fin_ANotification.objects.filter(status = 'New').order_by('-id','-Noti_date')
   n = len(noti)
   return render(request,"Admin/Fin_All_distributors.html",{'data':data,'noti':noti,'n':n})

def Fin_All_Distributor_Overview(request,id):
   data = Fin_Distributors_Details.objects.get(id=id)
   noti = Fin_ANotification.objects.filter(status = 'New').order_by('-id','-Noti_date')
   n = len(noti)
   return render(request,"Admin/Fin_All_Distributor_Overview.html",{'data':data,'noti':noti,'n':n})  

def Fin_AClients(request):
    noti = Fin_ANotification.objects.filter(status = 'New').order_by('-id','-Noti_date')
    n = len(noti)
    return render(request,"Admin/Fin_AClients.html",{'noti':noti,'n':n})


def Fin_AClients_Request(request):
    data = Fin_Company_Details.objects.filter(Registration_Type = "self", Admin_approval_status = "NULL")
    print(data)
    noti = Fin_ANotification.objects.filter(status = 'New').order_by('-id','-Noti_date')
    n = len(noti)
    return render(request,"Admin/Fin_AClients_Request.html",{'data':data,'noti':noti,'n':n})

def Fin_AClients_Request_OverView(request,id):
    data = Fin_Company_Details.objects.get(id=id)
    allmodules = Fin_Modules_List.objects.get(company_id = id,status = "New")
    noti = Fin_ANotification.objects.filter(status = 'New').order_by('-id','-Noti_date')
    n = len(noti)
    return render(request,'Admin/Fin_AClients_Request_OverView.html',{'data':data,'allmodules':allmodules,'noti':noti,'n':n})

def Fin_Client_Req_Accept(request,id):
   data = Fin_Company_Details.objects.get(id=id)
   data.Admin_approval_status = 'Accept'
   data.save()
   return redirect('Fin_AClients_Request')

def Fin_Client_Req_Reject(request,id):
   data = Fin_Company_Details.objects.get(id=id)
   data.Login_Id.delete()
   data.delete()
   return redirect('Fin_AClients_Request')

def Fin_Client_delete(request,id):
   data = Fin_Company_Details.objects.get(id=id)
   data.Login_Id.delete()
   data.delete()
   return redirect('Fin_Admin_clients')

def Fin_Admin_clients(request):
   data = Fin_Company_Details.objects.filter(Admin_approval_status = "Accept")
   print(data)
   noti = Fin_ANotification.objects.filter(status = 'New').order_by('-id','-Noti_date')
   n = len(noti)
   return render(request,"Admin/Fin_Admin_clients.html",{'data':data,'noti':noti,'n':n})

def Fin_Admin_clients_overview(request,id):
   data = Fin_Company_Details.objects.get(id=id)
   allmodules = Fin_Modules_List.objects.get(company_id = id,status = "New")
   noti = Fin_ANotification.objects.filter(status = 'New').order_by('-id','-Noti_date')
   n = len(noti)
   return render(request,"Admin/Fin_Admin_clients_overview.html",{'data':data,'allmodules':allmodules,'noti':noti,'n':n})   

def Fin_Anotification(request):
    noti = Fin_ANotification.objects.filter(status = 'New').order_by('-id','-Noti_date')
    n = len(noti)
    context = {
        'noti':noti,
        'n':n
    }
    return render(request,'Admin/Fin_Anotification.html',context) 

def  Fin_Anoti_Overview(request,id):
    noti = Fin_ANotification.objects.filter(status = 'New')
    n = len(noti)

    
    data = Fin_ANotification.objects.get(id=id)

    if data.Login_Id.User_Type == "Company":

        if data.Modules_List :
            allmodules = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "New")
            allmodules1 = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "pending")

            modules_pending = Fin_Modules_List.objects.filter(Login_Id = data.Login_Id,status = "pending")
            current_modules = Fin_Modules_List.objects.filter(Login_Id = data.Login_Id,status = "New")

            # Extract the field names related to modules
            module_fields = [field.name for field in Fin_Modules_List._meta.fields if field.name not in ['id', 'company', 'status', 'update_action','company_id', 'Login_Id' ]]

            # Get the previous and new values for the selected modules
            previous_values = current_modules.values(*module_fields).first()
            new_values = modules_pending.values(*module_fields).first()

            # Iterate through the dictionary and replace None with 0
            for key, value in previous_values.items():
                if value is None:
                    previous_values[key] = 0

            # Iterate through the dictionary and replace None with 0
            for key, value in new_values.items():
                if value is None:
                    new_values[key] = 0

            # Identify added and deducted modules
            added_modules = {}
            deducted_modules = {}

            for field in module_fields:
                if new_values[field] > previous_values[field]:
                    added_modules[field] = new_values[field] - previous_values[field]
                elif new_values[field] < previous_values[field]:
                    deducted_modules[field] = previous_values[field] - new_values[field]
            
           
            context = {
                'noti':noti,
                'n':n,
                'data':data,
                'allmodules':allmodules,
                'allmodules1':allmodules1,
                'current_modules': current_modules,
                'modules_pending': modules_pending,
                'previous_values': previous_values,
                'new_values': new_values,
                'added_modules': added_modules,
                'deducted_modules': deducted_modules,
            }
            return render(request,'Admin/Fin_Anoti_Overview.html',context)
        else:
            data1 = Fin_Company_Details.objects.get(Login_Id = data.Login_Id)
            context = {
                'noti':noti,
                'n':n,
                'data1':data1,
                'data':data,
                
            }
            return render(request,'Admin/Fin_Anoti_Overview.html',context)
    else:
        data1 = Fin_Distributors_Details.objects.get(Login_Id = data.Login_Id)
        context = {
                'noti':noti,
                'n':n,
                'data1':data1,
                'data':data,
                
            }

        return render(request,'Admin/Fin_Anoti_Overview.html',context)

def  Fin_Module_Updation_Accept(request,id):
    data = Fin_ANotification.objects.get(id=id)
    allmodules = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "New")
    allmodules.delete()

    allmodules1 = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "pending")
    allmodules1.status = "New"
    allmodules1.save()

    data.status = 'old'
    data.save()

    # notification
    notification=Fin_CNotification.objects.create(Login_Id=allmodules1.Login_Id, Company_id=allmodules1.company_id,Title='Modules Updated..!',Discription='Your module update request is approved')

    return redirect('Fin_Anotification')

def  Fin_Module_Updation_Reject(request,id):
    data = Fin_ANotification.objects.get(id=id)
    allmodules = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "pending")
    allmodules.delete()

    data.delete()

    return redirect('Fin_Anotification')

def  Fin_payment_terms_Updation_Accept(request,id):
    data = Fin_ANotification.objects.get(id=id)
    com = Fin_Company_Details.objects.get(Login_Id = data.Login_Id)
    terms=Fin_Payment_Terms.objects.get(id=data.PaymentTerms_updation.Payment_Term.id)

    title=['Trial Period Alert','Payment Terms Alert',]
    cnoti = Fin_CNotification.objects.filter(Company_id = com, Title__in=title)
    cnoti.update(status='old')

    anoti= Fin_ANotification.objects.filter(Login_Id = com.Login_Id, Title__in=title) 
    anoti.update(status='old')
    
    
    start=com.End_date + timedelta(days=1)
    com.Start_Date = start
    days=int(terms.days)

    end= start + timedelta(days=days)
    com.End_date = end
    com.Payment_Term = terms
    com.save()

    data.status = 'old'
    data.save()

    upt = Fin_Payment_Terms_updation.objects.get(id = data.PaymentTerms_updation.id)
    upt.status = 'old'
    upt.save()

    

    # notification
    message=f'Your new plan is activated and ends on {end}'
    notification=Fin_CNotification.objects.create(Login_Id=com.Login_Id, Company_id=com,Title='New Plan Activated..!',Discription=message)

    return redirect('Fin_Anotification')

def  Fin_payment_terms_Updation_Reject(request,id):
    data = Fin_ANotification.objects.get(id=id)

    upt = Fin_Payment_Terms_updation.objects.get(id = data.PaymentTerms_updation.id)

    upt.delete()
    data.delete()

    return redirect('Fin_Anotification')


def  Fin_ADpayment_terms_Updation_Accept(request,id):
    data = Fin_ANotification.objects.get(id=id)
    com = Fin_Distributors_Details.objects.get(Login_Id = data.Login_Id)
    terms=Fin_Payment_Terms.objects.get(id=data.PaymentTerms_updation.Payment_Term.id)
    
    start=com.End_date + timedelta(days=1)
    com.Start_Date =start
    days=int(terms.days)

    end= start + timedelta(days=days)
    com.End_date = end
    com.Payment_Term = terms
    com.save()

    data.status = 'old'
    data.save()

    upt = Fin_Payment_Terms_updation.objects.get(id = data.PaymentTerms_updation.id)
    upt.status = 'old'
    upt.save()

    title=['Trial Period Alert','Payment Terms Alert',]
    dnoti = Fin_DNotification.objects.filter(Distributor_id = com,Title__in=title)
    dnoti.update(status='old')

    anoti= Fin_ANotification.objects.filter(Login_Id = com.Login_Id, Title__in=title) 
    anoti.update(status='old')

    # notification
    message=f'Your new plan is activated and ends on {end}'
    notification=Fin_DNotification.objects.create(Login_Id=com.Login_Id, Distributor_id=com,Title='New Plan Activated..!',Discription=message)  

    return redirect('Fin_Anotification')


def  Fin_ADpayment_terms_Updation_Reject(request,id):
    data = Fin_ANotification.objects.get(id=id)

    upt = Fin_Payment_Terms_updation.objects.get(id = data.PaymentTerms_updation.id)

    upt.delete()
    data.delete()

    return redirect('Fin_Anotification')

 
# ---------------------------end admin ------------------------------------ 






# ---------------------------start distributor------------------------------------   

def Fin_DHome(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Distributors_Details.objects.get(Login_Id = s_id)
        current_day=date.today() 
        diff = (data.End_date - current_day).days
        num = 20

        payment_request=Fin_Payment_Terms_updation.objects.filter(Login_Id=data.Login_Id,status='New').exists()


        title2=['Modules Updated..!','New Plan Activated..!','Change Payment Terms']
        today_date = datetime.now().date()
        notification=Fin_DNotification.objects.filter(status = 'New',Distributor_id = data,Title__in=title2,Noti_date__lt=today_date)
        notification.update(status='old')

        dis_name=data.Login_Id.First_name +"  "+ data.Login_Id.Last_name
        if not Fin_DNotification.objects.filter(Login_Id = data.Login_Id,Distributor_id = data,Title="Payment Terms Alert", status = 'New').exists() and diff <= 20:
            n = Fin_DNotification(Login_Id=data.Login_Id, Distributor_id = data, Title="Payment Terms Alert", Discription="Your Payment Terms End Soon")
            n.save()
            d = Fin_ANotification(Login_Id=data.Login_Id, Title="Payment Terms Alert", Discription=f"Current  payment terms of {dis_name} is expiring")
            d.save()
        noti = Fin_DNotification.objects.filter(status = 'New',Distributor_id = data.id).order_by('-id','-Noti_date')
        n = len(noti)
        
        # Calculate the date 20 days before the end date for payment term renew
        reminder_date = data.End_date - timedelta(days=20)    
        current_date = date.today()
        alert_message = current_date >= reminder_date
        
        # Calculate the number of days between the reminder date and end date
        days_left = (data.End_date - current_date).days
          
        context = {
            'noti':noti,
            'n':n,
            'data':data,
            'alert_message':alert_message,
            'days_left':days_left,
            'payment_request':payment_request,
        }
        return render(request,'Distributor/Fin_DHome.html',context)
    else:
       return redirect('/')   
 

def Fin_DistributorReg(request):
    terms = Fin_Payment_Terms.objects.all()
    context = {
       'terms':terms
    }
    return render(request,'Distributor/Fin_DistributorReg.html',context)

def Fin_DReg_Action(request):
    if request.method == 'POST':
      first_name = request.POST['first_name']
      last_name = request.POST['last_name']
      email = request.POST['email']
      user_name = request.POST['username']
      password = request.POST['dpassword']

      if Fin_Login_Details.objects.filter(User_name=user_name).exists():
        messages.info(request, 'This username already exists. Sign up again')
        return redirect('Fin_DistributorReg')
      
      elif Fin_Distributors_Details.objects.filter(Email=email).exists():
        messages.info(request, 'This email already exists. Sign up again')
        return redirect('Fin_DistributorReg')
      else:
        dlog = Fin_Login_Details(First_name = first_name,Last_name = last_name,
                                User_name = user_name,password = password,
                                User_Type = 'Distributor')
        dlog.save()

        code_length = 8  
        characters = string.ascii_letters + string.digits  # Letters and numbers

        while True:
            unique_code = ''.join(random.choice(characters) for _ in range(code_length))
        
            # Check if the code already exists in the table
            if not Fin_Company_Details.objects.filter(Company_Code = unique_code).exists():
              break 

        ddata = Fin_Distributors_Details(Email = email,Login_Id = dlog,Distributor_Code = unique_code,Admin_approval_status = "NULL")
        ddata.save()
        return redirect('Fin_DReg2',dlog.id)    

        # code=get_random_string(length=6)
        # if Fin_Distributors_Details.objects.filter( Distributor_Code = code).exists():
        #     code2=get_random_string(length=6)

        #     ddata = Fin_Distributors_Details(Email = email,Login_Id = dlog,Distributor_Code = code2,Admin_approval_status = "NULL")
        #     ddata.save()
        #     return redirect('Fin_DReg2',dlog.id)
        # else:
        #     ddata = Fin_Distributors_Details(Email = email,Login_Id = dlog,Distributor_Code = code,Admin_approval_status = "NULL")
        #     ddata.save()
        #     return redirect('Fin_DReg2',dlog.id)
 
    return redirect('Fin_DistributorReg')

def Fin_DReg2(request,id):
    dlog = Fin_Login_Details.objects.get(id = id)
    ddata = Fin_Distributors_Details.objects.get(Login_Id = id)
    terms = Fin_Payment_Terms.objects.all()
    context = {
       'terms':terms,
       'dlog':dlog,
       'ddata':ddata
    }
    return render(request,'Distributor/Fin_DReg2.html',context)

def Fin_DReg2_Action2(request,id):
   if request.method == 'POST':
      ddata = Fin_Distributors_Details.objects.get(Login_Id = id)

      ddata.Contact = request.POST['phone']
      ddata.Image=request.FILES.get('img')

      payment_term = request.POST['payment_term']
      terms=Fin_Payment_Terms.objects.get(id=payment_term)
    
      start_date=date.today()
      days=int(terms.days)

      end= date.today() + timedelta(days=days)
      End_date=end

      ddata.Payment_Term  = terms
      ddata.Start_Date = start_date
      ddata.End_date = End_date

      ddata.save()
      return redirect('Fin_DistributorReg')
   return render('Fin_DReg2',id)  

def Fin_DClient_req(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Distributors_Details.objects.get(Login_Id = s_id)
        data1 = Fin_Company_Details.objects.filter(Registration_Type = "distributor",Distributor_approval_status = "NULL",Distributor_id = data.id)
        noti = Fin_DNotification.objects.filter(status = 'New',Distributor_id = data.id)
        n = len(noti)
        return render(request,'Distributor/Fin_DClient_req.html',{'data':data,'data1':data1,'noti':noti,'n':n})
    else:
       return redirect('/') 
    
def Fin_DClient_req_overview(request,id):
    data = Fin_Company_Details.objects.get(id=id)
    allmodules = Fin_Modules_List.objects.get(company_id = id,status = "New")
    noti = Fin_DNotification.objects.filter(status = 'New',Distributor_id = data.id)
    n = len(noti)
    return render(request,'Distributor/Fin_DClient_req_overview.html',{'data':data,'allmodules':allmodules,'noti':noti,'n':n})    
    
def Fin_DClient_Req_Accept(request,id):
   data = Fin_Company_Details.objects.get(id=id)
   data.Distributor_approval_status = 'Accept'
   data.save()
   return redirect('Fin_DClient_req')

def Fin_DClient_Req_Reject(request,id):
   data = Fin_Company_Details.objects.get(id=id)
   data.Login_Id.delete()
   data.delete()
   return redirect('Fin_DClient_req')   

def Fin_DClients(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Distributors_Details.objects.get(Login_Id = s_id)
        data1 = Fin_Company_Details.objects.filter(Registration_Type = "distributor",Distributor_approval_status = "Accept",Distributor_id = data.id)
        noti = Fin_DNotification.objects.filter(status = 'New',Distributor_id = data.id)
        n = len(noti)
        return render(request,'Distributor/Fin_DClients.html',{'data':data,'data1':data1,'noti':noti,'n':n})
    else:
       return redirect('/')  
   
def Fin_DClients_overview(request,id):
    data = Fin_Company_Details.objects.get(id=id)
    allmodules = Fin_Modules_List.objects.get(company_id = id,status = "New")
    noti = Fin_DNotification.objects.filter(status = 'New',Distributor_id = data.id)
    n = len(noti)
    return render(request,'Distributor/Fin_DClients_overview.html',{'data':data,'allmodules':allmodules,'noti':noti,'n':n})

def Fin_DClient_remove(request,id):
   data = Fin_Company_Details.objects.get(id=id)
   data.Login_Id.delete()
   data.delete()
   return redirect('Fin_DClients') 
    
def Fin_DProfile(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Distributors_Details.objects.get(Login_Id = s_id)
        data1 = Fin_Company_Details.objects.filter(Registration_Type = "distributor",Distributor_approval_status = "Accept",Distributor_id = data.id)
        terms = Fin_Payment_Terms.objects.all()

        payment_request=Fin_Payment_Terms_updation.objects.filter(Login_Id=data.Login_Id,status='New').exists()


        noti = Fin_DNotification.objects.filter(status = 'New',Distributor_id = data.id)
        n = len(noti)
        return render(request,'Distributor/Fin_DProfile.html',{'data':data,'data1':data1,'terms':terms,'noti':noti,'n':n,'payment_request':payment_request})
    else:
       return redirect('/')   
    
def Fin_Dnotification(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Distributors_Details.objects.get(Login_Id = s_id)

        noti = Fin_DNotification.objects.filter(status = 'New',Distributor_id = data.id).order_by('-id','-Noti_date')
        n = len(noti)
        context = {
            'noti':noti,
            'n':n,
            'data':data
        }
        return render(request,'Distributor/Fin_Dnotification.html',context)  
    else:
       return redirect('/') 
    

def  Fin_Dnoti_Overview(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        d = Fin_Distributors_Details.objects.get(Login_Id = s_id)
        noti = Fin_DNotification.objects.filter(status = 'New',Distributor_id = d.id)
        n = len(noti)

        

        data = Fin_DNotification.objects.get(id=id)

        if data.Modules_List :
            allmodules = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "New")
            allmodules1 = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "pending")

            modules_pending = Fin_Modules_List.objects.filter(Login_Id = data.Login_Id,status = "pending")
            current_modules = Fin_Modules_List.objects.filter(Login_Id = data.Login_Id,status = "New")

            # Extract the field names related to modules
            module_fields = [field.name for field in Fin_Modules_List._meta.fields if field.name not in ['id', 'company', 'status', 'update_action','company_id', 'Login_Id' ]]

            # Get the previous and new values for the selected modules
            previous_values = current_modules.values(*module_fields).first()
            new_values = modules_pending.values(*module_fields).first()

            # Iterate through the dictionary and replace None with 0
            for key, value in previous_values.items():
                if value is None:
                    previous_values[key] = 0

            # Iterate through the dictionary and replace None with 0
            for key, value in new_values.items():
                if value is None:
                    new_values[key] = 0

            # Identify added and deducted modules
            added_modules = {}
            deducted_modules = {}

            for field in module_fields:
                if new_values[field] > previous_values[field]:
                    added_modules[field] = new_values[field] - previous_values[field]
                elif new_values[field] < previous_values[field]:
                    deducted_modules[field] = previous_values[field] - new_values[field]


            context = {
                'noti':noti,
                'n':n,
                'data':data,
                'allmodules':allmodules,
                'allmodules1':allmodules1,
                'current_modules': current_modules,
                'modules_pending': modules_pending,
                'previous_values': previous_values,
                'new_values': new_values,
                'added_modules': added_modules,
                'deducted_modules': deducted_modules,
            }
            return render(request,'Distributor/Fin_Dnoti_Overview.html',context)

        else:
            data1 = Fin_Company_Details.objects.get(Login_Id = data.Login_Id)
            context = {
                'noti':noti,
                'n':n,
                'data1':data1,
                'data':data,
                
            }
            return render(request,'Distributor/Fin_Dnoti_Overview.html',context)    
    else:
       return redirect('/') 


def  Fin_DModule_Updation_Accept(request,id):
    data = Fin_DNotification.objects.get(id=id)
    allmodules = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "New")
    allmodules.delete()

    allmodules1 = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "pending")
    allmodules1.status = "New"
    allmodules1.save()

    data.status = 'old'
    data.save()

    # notification
    notification=Fin_CNotification.objects.create(Login_Id=allmodules1.Login_Id, Company_id=allmodules1.company_id,Title='Modules Updated..!',Discription='Your module update request is approved')

    return redirect('Fin_Dnotification')


def  Fin_DModule_Updation_Reject(request,id):
    data = Fin_DNotification.objects.get(id=id)
    allmodules = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "pending")
    allmodules.delete()

    data.delete()

    return redirect('Fin_Dnotification')


def  Fin_Dpayment_terms_Updation_Accept(request,id):
    data = Fin_DNotification.objects.get(id=id)
    com = Fin_Company_Details.objects.get(Login_Id = data.Login_Id)
    terms=Fin_Payment_Terms.objects.get(id=data.PaymentTerms_updation.Payment_Term.id)

    title=['Trial Period Alert','Payment Terms Alert']
    cnoti = Fin_CNotification.objects.filter(Company_id = com, Title__in=title)
    dnoti = Fin_DNotification.objects.filter(Distributor_id = com.Distributor_id,Login_Id=com.Login_Id,Title__in=title)
    dnoti.update(status='old')

    
    for c in cnoti:
        c.status = 'old'
        c.save()  
    
    start=com.End_date + timedelta(days=1)
    com.Start_Date = start
    days=int(terms.days)

    end= start + timedelta(days=days)
    com.End_date = end
    com.Payment_Term = terms
    com.save()

    data.status = 'old'
    data.save()

    upt = Fin_Payment_Terms_updation.objects.get(id = data.PaymentTerms_updation.id)
    upt.status = 'old'
    upt.save()

    # notification
    message=f'Your new plan is activated and ends on {end}'
    notification=Fin_CNotification.objects.create(Login_Id=com.Login_Id, Company_id=com,Title='New Plan Activated..!',Discription=message)

    return redirect('Fin_Dnotification')


def  Fin_Dpayment_terms_Updation_Reject(request,id):
    data = Fin_DNotification.objects.get(id=id)

    upt = Fin_Payment_Terms_updation.objects.get(id = data.PaymentTerms_updation.id)

    upt.delete()
    data.delete()

    return redirect('Fin_Dnotification')    


def Fin_DChange_payment_terms(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        
        if request.method == 'POST':
            data = Fin_Login_Details.objects.get(id = s_id)
            com = Fin_Distributors_Details.objects.get(Login_Id = s_id)
            pt = request.POST['payment_term']

            if Fin_Payment_Terms_updation.objects.filter(Login_Id=com.Login_Id,status='New').exists():
                return redirect('Fin_DProfile')

            pay = Fin_Payment_Terms.objects.get(id=pt)

            data1 = Fin_Payment_Terms_updation(Login_Id = data,Payment_Term = pay)
            data1.save()

            
            noti = Fin_ANotification(Login_Id = data,PaymentTerms_updation = data1,Title = "Change Payment Terms",Discription = com.Login_Id.First_name + ' ' + com.Login_Id.Last_name + " wants to subscribe a new plan")
            noti.save()
              


        
            return redirect('Fin_DProfile')
    else:
       return redirect('/') 


def Fin_Edit_Dprofile(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        com = Fin_Distributors_Details.objects.get(Login_Id = s_id)
        data = Fin_Distributors_Details.objects.get(Login_Id = s_id)

        noti = Fin_DNotification.objects.filter(status = 'New',Distributor_id = data.id)
        n = len(noti)

        context ={
            'com':com,
            'data':data,
            'n':n,
            'noti':noti
        }

        return render(request,"Distributor/Fin_Edit_Dprofile.html",context)    
    else:
       return redirect('/')    
    
def Fin_Edit_Dprofile_Action(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        com = Fin_Distributors_Details.objects.get(Login_Id = s_id)
        if request.method == 'POST':
            com.Login_Id.First_name = request.POST['first_name']
            com.Login_Id.Last_name = request.POST['last_name']
            com.Email = request.POST['email']
            com.Contact = request.POST['contact']
            
            com.Image  = request.FILES.get('img')
            

            com.Login_Id.save()
            com.save()

            return redirect('Fin_DProfile')
        return redirect('Fin_Edit_Dprofile')     
    else:
       return redirect('/')     

      
# ---------------------------end distributor------------------------------------  


             
# ---------------------------start staff------------------------------------   
    

def Fin_StaffReg(request):
    return render(request,'company/Fin_StaffReg.html')

def Fin_staffReg_action(request):
   if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        user_name = request.POST['cusername']
        password = request.POST['cpassword'] 
        cid = request.POST['Company_Code']
        if Fin_Company_Details.objects.filter(Company_Code = cid ).exists():
            com =Fin_Company_Details.objects.get(Company_Code = cid )

            if Fin_Staff_Details.objects.filter(company_id=com,Login_Id__User_name=user_name).exists():
                messages.info(request, 'This username already exists. Sign up again')
                return redirect('Fin_StaffReg')

            if Fin_Login_Details.objects.filter(User_name=user_name,password = password).exists():
                messages.info(request, 'This username and password already exists. Sign up again')
                return redirect('Fin_StaffReg')
        
            elif Fin_Staff_Details.objects.filter(Email=email).exists():
                messages.info(request, 'This email already exists. Sign up again')
                return redirect('Fin_StaffReg')
            else:
                dlog = Fin_Login_Details(First_name = first_name,Last_name = last_name,
                                    User_name = user_name,password = password,
                                    User_Type = 'Staff')
                dlog.save()

                ddata = Fin_Staff_Details(Email = email,Login_Id = dlog,Company_approval_status = "NULL",company_id = com)
                ddata.save()
                return redirect('Fin_StaffReg2',dlog.id)
        else:
            messages.info(request, 'This company code  not exists. Sign up again')  
            return redirect('Fin_StaffReg')    
        
def Fin_StaffReg2(request,id):
    dlog = Fin_Login_Details.objects.get(id = id)
    ddata = Fin_Staff_Details.objects.get(Login_Id = id)
    context = {
       'dlog':dlog,
       'ddata':ddata
    }
    return render(request,'company/Fin_StaffReg2.html',context)

def Fin_StaffReg2_Action(request,id):
    if request.method == 'POST':
        
        staff = Fin_Staff_Details.objects.get(Login_Id = id)
        log = Fin_Login_Details.objects.get(id = id)

        staff.Login_Id = log
           
        staff.contact = request.POST['phone']
        staff.img=request.FILES.get('img')
        staff.Company_approval_status = "Null"
        staff.save()
        print("Staff Registration Complete")
    
        return redirect('Fin_StaffReg')
        
    else:
        return redirect('Fin_StaffReg2',id)
# ---------------------------end staff------------------------------------ 


    
# ---------------------------start company------------------------------------ 

def Fin_Com_Home(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')

            payment_request=Fin_Payment_Terms_updation.objects.filter(Login_Id=com.Login_Id,status='New').exists()


            title2=['Modules Updated..!','New Plan Activated..!']
            today_date = datetime.now().date()
            notification=Fin_CNotification.objects.filter(status = 'New',Company_id = com,Title__in=title2,Noti_date__lt=today_date).order_by('-id','-Noti_date')
            notification.update(status='old')

            current_day=date.today() 
            diff = (com.End_date - current_day).days
            
            # payment term and trial period alert notifications for notifation page
            cmp_name=com.Company_name
            if com.Payment_Term:
                if not Fin_CNotification.objects.filter(Company_id=com, Title="Payment Terms Alert",status = 'New').exists() and diff <= 20:
                    
                    n = Fin_CNotification(Login_Id=data, Company_id=com, Title="Payment Terms Alert", Discription="Your Payment Terms End Soon")
                    n.save()
                    if com.Registration_Type == 'self':
                        d = Fin_ANotification(Login_Id=data, Title="Payment Terms Alert", Discription=f"Current  payment terms of {cmp_name} is expiring")
                    else:
                        d = Fin_DNotification(Login_Id=data, Distributor_id=com.Distributor_id, Title="Payment Terms Alert", Discription=f"Current  payment terms of {cmp_name} is expiring")

                    d.save()
            else:
                if not Fin_CNotification.objects.filter(Company_id=com, Title="Trial Period Alert",status = 'New').exists() and diff <= 10:
                    n = Fin_CNotification(Login_Id=data, Company_id=com, Title="Trial Period Alert", Discription="Your Trial Period End Soon")
                    n.save()
                    if com.Registration_Type == 'self':
                        d = Fin_ANotification(Login_Id=data, Title="Payment Terms Alert", Discription=f"Current  payment terms of {cmp_name} is expiring")
                    else:
                        d = Fin_DNotification(Login_Id=data, Distributor_id=com.Distributor_id, Title="Payment Terms Alert", Discription=f"Current  payment terms of {cmp_name} is expiring")

                    d.save()

            noti = Fin_CNotification.objects.filter(status = 'New',Company_id = com).order_by('-id','-Noti_date')
            n = len(noti)

            # Calculate the date 20 days before the end date for payment term renew and 10 days before for trial period renew
            if com.Payment_Term:
                reminder_date = com.End_date - timedelta(days=20)
            else:
                reminder_date = com.End_date - timedelta(days=10)
            current_date = date.today()
            alert_message = current_date >= reminder_date
            
            # Calculate the number of days between the reminder date and end date
            days_left = (com.End_date - current_date).days

            context = {
                'allmodules':allmodules,
                'com':com,
                'data':data,
                'noti':noti,
                'n':n,
                'alert_message':alert_message,
                'days_left':days_left,
                'payment_request':payment_request,
                }

            return render(request,'company/Fin_Com_Home.html',context)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            return render(request,'company/Fin_Com_Home.html',{'allmodules':allmodules,'com':com,'data':data})
    else:
       return redirect('/') 


def Fin_Cnotification(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')


            title=['Trial Period Alert','Payment Terms Alert']
            title2=['Modules Updated..!','New Plan Activated..!']
            today_date = datetime.now().date()
            notification=Fin_CNotification.objects.filter(status = 'New',Company_id = com,Title__in=title2,Noti_date__lt=today_date).order_by('-id','-Noti_date')
            notification.update(status='old')

            noti = Fin_CNotification.objects.filter(status = 'New',Company_id = com).order_by('-id','-Noti_date')
            n = len(noti)

            payment_term_notification=Fin_CNotification.objects.filter(status = 'New',Company_id = com,Title__in=title).order_by('-id','-Noti_date')
            other_notification=Fin_CNotification.objects.filter(status = 'New',Company_id = com,Title__in=title2,date_created=today_date).order_by('-id','-Noti_date')
           

            
            context = {
                'allmodules':allmodules,
                'com':com,
                'data':data,
                'noti':noti,
                'n':n,
                'payment_term_notification':payment_term_notification,
                'other_notification':other_notification,
                
            }
            return render(request,'company/Fin_Cnotification.html',context)  
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            context = {
                'allmodules':allmodules,
                'com':com,
                'data':data,
                
            }
            return render(request,'company/Fin_Cnotification.html',context)
    else:
       return redirect('/')     

     

def Fin_CompanyReg(request):
    return render(request,'company/Fin_CompanyReg.html')

def Fin_companyReg_action(request):
   if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        user_name = request.POST['cusername']
        password = request.POST['cpassword']


        if Fin_Login_Details.objects.filter(User_name=user_name).exists():
            messages.info(request, 'This username already exists. Sign up again')
            return redirect('Fin_CompanyReg')
      
        elif Fin_Company_Details.objects.filter(Email=email).exists():
            messages.info(request, 'This email already exists. Sign up again')
            return redirect('Fin_CompanyReg')
        else:
            dlog = Fin_Login_Details(First_name = first_name,Last_name = last_name,
                                User_name = user_name,password = password,
                                User_Type = 'Company')
            dlog.save()

        code_length = 8  
        characters = string.ascii_letters + string.digits  # Letters and numbers

        while True:
            unique_code = ''.join(random.choice(characters) for _ in range(code_length))
        
            # Check if the code already exists in the table
            if not Fin_Company_Details.objects.filter(Company_Code = unique_code).exists():
              break  

        ddata = Fin_Company_Details(Email = email,Login_Id = dlog,Company_Code = unique_code,Admin_approval_status = "NULL",Distributor_approval_status = "NULL")
        ddata.save()
        return redirect('Fin_CompanyReg2',dlog.id)      

        # code=get_random_string(length=6)
        # if Fin_Company_Details.objects.filter( Company_Code = code).exists():
        #     code2=get_random_string(length=6)

        #     ddata = Fin_Company_Details(Email = email,Login_Id = dlog,Company_Code = code2,Admin_approval_status = "NULL",Distributor_approval_status = "NULL")
        #     ddata.save()
        #     return redirect('Fin_CompanyReg2',dlog.id)
        # else:
        #     ddata = Fin_Company_Details(Email = email,Login_Id = dlog,Company_Code = code,Admin_approval_status = "NULL",Distributor_approval_status = "NULL")
        #     ddata.save()
        #     return redirect('Fin_CompanyReg2',dlog.id)
 
   return redirect('Fin_DistributorReg')

def Fin_CompanyReg2(request,id):
    data = Fin_Login_Details.objects.get(id=id)
    terms = Fin_Payment_Terms.objects.all()
    return render(request,'company/Fin_CompanyReg2.html',{'data':data,'terms':terms})


def Fin_CompanyReg2_action2(request,id):
    if request.method == 'POST':
        data = Fin_Login_Details.objects.get(id=id)
        com = Fin_Company_Details.objects.get(Login_Id=data.id)

        com.Company_name = request.POST['cname']
        com.Address = request.POST['caddress']
        com.City = request.POST['city']
        com.State = request.POST['state']
        com.Pincode = request.POST['pincode']
        com.Country = request.POST['ccountry']
        com.Image  = request.FILES.get('img1')
        com.Business_name = request.POST['bname']
        com.Industry = request.POST['industry']
        com.Company_Type = request.POST['ctype']
        com.Accountant = request.POST['staff']
        com.Payment_Type = request.POST['paid']
        com.Registration_Type = request.POST['reg_type']
        com.Contact = request.POST['phone']

        dis_code = request.POST['dis_code']
        if dis_code != '':
            if Fin_Distributors_Details.objects.filter(Distributor_Code = dis_code).exists():
                com.Distributor_id = Fin_Distributors_Details.objects.get(Distributor_Code = dis_code)
            else :
                messages.info(request, 'Sorry, distributor id does not exists')
                return redirect('Fin_CompanyReg2',id)
            
        
        # Create a Trial period instance and save to company details
        com.Start_Date=date.today()
        days=int(30)
        end= date.today() + timedelta(days=days)
        com.End_date=end
        com.save()

        # Create a Trial period instance and populate it with form data
        trial_period=TrialPeriod(
            company=com,
            start_date=date.today(),
            end_date=end
        )
        trial_period.save() # Save the instance to the database

        return redirect('Fin_Modules',id)

   
def Fin_Modules(request,id):
    data = Fin_Login_Details.objects.get(id=id)
    return render(request,'company/Fin_Modules.html',{'data':data})    

def Fin_Add_Modules(request,id):
    if request.method == 'POST':
        data = Fin_Login_Details.objects.get(id=id)
        com = Fin_Company_Details.objects.get(Login_Id=data.id)

        # -----ITEMS----

        Items = request.POST.get('c1')
        Price_List = request.POST.get('c2')
        Stock_Adjustment = request.POST.get('c3')


        # --------- CASH & BANK-----
        Cash_in_hand = request.POST.get('c4')
        Offline_Banking = request.POST.get('c5')
        Bank_Reconciliation = request.POST.get('c6')
        UPI = request.POST.get('c7')
        Bank_Holders = request.POST.get('c8')
        Cheque = request.POST.get('c9')
        Loan_Account = request.POST.get('c10')

        #  ------SALES MODULE -------
        Customers = request.POST.get('c11')
        Invoice  = request.POST.get('c12')
        Estimate = request.POST.get('c13')
        Sales_Order = request.POST.get('c14')
        Recurring_Invoice = request.POST.get('c15')
        Retainer_Invoice = request.POST.get('c16')
        Credit_Note = request.POST.get('c17')
        Payment_Received = request.POST.get('c18')
        Delivery_Challan = request.POST.get('c19')

        #  ---------PURCHASE MODULE--------- 
        Vendors = request.POST.get('c20') 
        Bills  = request.POST.get('c21')
        Recurring_Bills = request.POST.get('c22')
        Debit_Note = request.POST.get('c23')
        Purchase_Order = request.POST.get('c24')
        Expenses = request.POST.get('c25')
        Recurring_Expenses = request.POST.get('c26')
        Payment_Made = request.POST.get('c27')
        EWay_Bill = request.POST.get('c28')

        #  -------ACCOUNTS--------- 
        Chart_of_Accounts = request.POST.get('c29') 
        Manual_Journal = request.POST.get('c30')
        Reconcile  = request.POST.get('c36')


        # -------PAYROLL------- 
        Employees = request.POST.get('c31')
        Employees_Loan = request.POST.get('c32')
        Holiday = request.POST.get('c33') 
        Attendance = request.POST.get('c34')
        Salary_Details = request.POST.get('c35')

        modules = Fin_Modules_List(Items = Items,Price_List = Price_List,Stock_Adjustment = Stock_Adjustment,
            Cash_in_hand = Cash_in_hand,Offline_Banking = Offline_Banking,Bank_Reconciliation = Bank_Reconciliation ,
            UPI = UPI,Bank_Holders = Bank_Holders,Cheque = Cheque,Loan_Account = Loan_Account,
            Customers = Customers,Invoice = Invoice,Estimate = Estimate,Sales_Order = Sales_Order,
            Recurring_Invoice = Recurring_Invoice,Retainer_Invoice = Retainer_Invoice,Credit_Note = Credit_Note,
            Payment_Received = Payment_Received,Delivery_Challan = Delivery_Challan,
            Vendors = Vendors,Bills = Bills,Recurring_Bills = Recurring_Bills,Debit_Note = Debit_Note,
            Purchase_Order = Purchase_Order,Expenses = Expenses,Recurring_Expenses = Recurring_Expenses,
            Payment_Made = Payment_Made,EWay_Bill = EWay_Bill,
            Chart_of_Accounts = Chart_of_Accounts,Manual_Journal = Manual_Journal,Reconcile = Reconcile ,
            Employees = Employees,Employees_Loan = Employees_Loan,Holiday = Holiday,
            Attendance = Attendance,Salary_Details = Salary_Details,
            Login_Id = data,company_id = com)
        
        modules.save()

        #Adding Default Units under company
        Fin_Units.objects.create(Company=com, name='BOX')
        Fin_Units.objects.create(Company=com, name='NUMBER')
        Fin_Units.objects.create(Company=com, name='PACK')


        #Adding Default loan terms under company by TINTO MT
        Fin_Loan_Term.objects.create(company=com, duration=3,term='MONTH',days=90)
        Fin_Loan_Term.objects.create(company=com, duration='6',term='MONTH',days=180)
        Fin_Loan_Term.objects.create(company=com, duration=1,term='YEAR',days=365)

        # Adding default accounts for companies

        created_date = date.today()
        account_info = [
            {"company_id": com, "Login_Id": data, "account_type": "Accounts Payable", "account_name": "Accounts Payable", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "This is an account of all the money which you owe to others like a pending bill payment to a vendor,etc.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Accounts Receivable", "account_name": "Accounts Receivable", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "The money that customers owe you becomes the accounts receivable. A good example of this is a payment expected from an invoice sent to your customer.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Asset", "account_name": "Advance Tax", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Any tax which is paid in advance is recorded into the advance tax account. This advance tax payment could be a quarterly, half yearly or yearly payment", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Advertising and Marketing", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Your expenses on promotional, marketing and advertising activities like banners, web-adds, trade shows, etc. are recorded in advertising and marketing account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Automobile Expense", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Transportation related expenses like fuel charges and maintenance charges for automobiles, are included to the automobile expense account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Bad Debt", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Any amount which is lost and is unrecoverable is recorded into the bad debt account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Bank Fees and Charges", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": " Any bank fees levied is recorded into the bank fees and charges account. A bank account maintenance fee, transaction charges, a late payment fee are some examples.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Consultant Expense", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Charges for availing the services of a consultant is recorded as a consultant expenses. The fees paid to a soft skills consultant to impart personality development training for your employees is a good example.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Cost Of Goods Sold", "account_name": "Cost of Goods Sold", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An expense account which tracks the value of the goods sold.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Credit Card Charges", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": " Service fees for transactions , balance transfer fees, annual credit fees and other charges levied on a credit card are recorded into the credit card account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Depreciation Expense", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Any depreciation in value of your assets can be captured as a depreciation expense.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Income", "account_name": "Discount", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Any reduction on your selling price as a discount can be recorded into the discount account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Equity", "account_name": "Drawings", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "The money withdrawn from a business by its owner can be tracked with this account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Asset", "account_name": "Employee Advance", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Money paid out to an employee in advance can be tracked here till it's repaid or shown to be spent for company purposes", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Liability", "account_name": "Employee Reimbursements", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "This account can be used to track the reimbursements that are due to be paid out to employees.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Expense", "account_name": "Exchange Gain or Loss", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Changing the conversion rate can result in a gain or a loss. You can record this into the exchange gain or loss account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Fixed Asset", "account_name": "Furniture and Equipment", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Purchases of furniture and equipment for your office that can be used for a long period of time usually exceeding one year can be tracked with this account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Income", "account_name": "General Income", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "A general category of account where you can record any income which cannot be recorded into any other category", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Income", "account_name": "Interest Income", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "A percentage of your balances and deposits are given as interest to you by your banks and financial institutions. This interest is recorded into the interest income account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Stock", "account_name": "Inventory Asset", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An account which tracks the value of goods in your inventory.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "IT and Internet Expenses", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Money spent on your IT infrastructure and usage like internet connection, purchasing computer equipment etc is recorded as an IT and Computer Expense", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Janitorial Expense", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "All your janitorial and cleaning expenses are recorded into the janitorial expenses account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Income", "account_name": "Late Fee Income", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Any late fee income is recorded into the late fee income account. The late fee is levied when the payment for an invoice is not received by the due date", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Lodging", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Any expense related to putting up at motels etc while on business travel can be entered here.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Meals and Entertainment", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Expenses on food and entertainment are recorded into this account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Office Supplies", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "All expenses on purchasing office supplies like stationery are recorded into the office supplies account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Other Current Liability", "account_name": "Opening Balance Adjustments", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "This account will hold the difference in the debits and credits entered during the opening balance.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Equity", "account_name": "Opening Balance Offset", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "This is an account where you can record the balance from your previous years earning or the amount set aside for some activities. It is like a buffer account for your funds.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Income", "account_name": "Other Charges", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Miscellaneous charges like adjustments made to the invoice can be recorded in this account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Other Expenses", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": " Any minor expense on activities unrelated to primary business operations is recorded under the other expense account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Equity", "account_name": "Owner's Equity", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "The owners rights to the assets of a company can be quantified in the owner's equity account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Cash", "account_name": "Petty Cash", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "It is a small amount of cash that is used to pay your minor or casual expenses rather than writing a check.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Postage", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Your expenses on ground mails, shipping and air mails can be recorded under the postage account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Asset", "account_name": "Prepaid Expenses", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An asset account that reports amounts paid in advance while purchasing goods or services from a vendor.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Printing and Stationery", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": " Expenses incurred by the organization towards printing and stationery.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Rent Expense", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "The rent paid for your office or any space related to your business can be recorded as a rental expense.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Repairs and Maintenance", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "The costs involved in maintenance and repair of assets is recorded under this account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Equity", "account_name": "Retained Earnings", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "The earnings of your company which are not distributed among the share holders is accounted as retained earnings.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Salaries and Employee Wages", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Salaries for your employees and the wages paid to workers are recorded under the salaries and wages account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Income", "account_name": "Sales", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": " The income from the sales in your business is recorded under the sales account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Income", "account_name": "Shipping Charge", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Shipping charges made to the invoice will be recorded in this account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Other Liability", "account_name": "Tag Adjustments", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": " This adjustment account tracks the transfers between different reporting tags.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Liability", "account_name": "Tax Payable", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "The amount of money which you owe to your tax authority is recorded under the tax payable account. This amount is a sum of your outstanding in taxes and the tax charged on sales.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Telephone Expense", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "The expenses on your telephone, mobile and fax usage are accounted as telephone expenses.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Travel Expense", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": " Expenses on business travels like hotel bookings, flight charges, etc. are recorded as travel expenses.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Uncategorized", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "This account can be used to temporarily track expenses that are yet to be identified and classified into a particular category.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Cash", "account_name": "Undeposited Funds", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Record funds received by your company yet to be deposited in a bank as undeposited funds and group them as a current asset in your balance sheet.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Liability", "account_name": "Unearned Revenue", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "A liability account that reports amounts received in advance of providing goods or services. When the goods or services are provided, this account balance is decreased and a revenue account is increased.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Equity", "account_name": "Capital Stock", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": " An equity account that tracks the capital introduced when a business is operated through a company or corporation.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Long Term Liability", "account_name": "Construction Loans", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An expense account that tracks the amount you repay for construction loans.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Contract Assets", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An asset account to track the amount that you receive from your customers while you're yet to complete rendering the services.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Depreciation And Amortisation", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An expense account that is used to track the depreciation of tangible assets and intangible assets, which is amortization.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Equity", "account_name": "Distributions", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An equity account that tracks the payment of stock, cash or physical products to its shareholders.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Equity", "account_name": "Dividends Paid", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An equity account to track the dividends paid when a corporation declares dividend on its common stock.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Other Current Liability", "account_name": "GST Payable", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Liability", "account_name": "Output CGST", "credit_card_no": "", "sub_account": True, "parent_account": "GST Payable", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Liability", "account_name": "Output IGST", "credit_card_no": "", "sub_account": True, "parent_account": "GST Payable", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Liability", "account_name": "Output SGST", "credit_card_no": "", "sub_account": True, "parent_account": "GST Payable", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Other Current Asset", "account_name": "GST TCS Receivable", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Asset", "account_name": "GST TDS Receivable", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Other Current Asset", "account_name": "Input Tax Credits", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Asset", "account_name": "Input CGST", "credit_card_no": "", "sub_account": True, "parent_account": "Input Tax Credits", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Asset", "account_name": "Input IGST", "credit_card_no": "", "sub_account": True, "parent_account": "Input Tax Credits", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Asset", "account_name": "Input SGST", "credit_card_no": "", "sub_account": True, "parent_account": "Input Tax Credits", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Equity", "account_name": "Investments", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An equity account used to track the amount that you invest.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Cost Of Goods Sold", "account_name": "Job Costing", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An expense account to track the costs that you incur in performing a job or a task.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Cost Of Goods Sold", "account_name": "Labor", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An expense account that tracks the amount that you pay as labor.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Cost Of Goods Sold", "account_name": "Materials", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An expense account that tracks the amount you use in purchasing materials.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Merchandise", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An expense account to track the amount spent on purchasing merchandise.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Long Term Liability", "account_name": "Mortgages", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An expense account that tracks the amounts you pay for the mortgage loan.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Raw Materials And Consumables", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An expense account to track the amount spent on purchasing raw materials and consumables.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Asset", "account_name": "Reverse Charge Tax Input but not due", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "The amount of tax payable for your reverse charge purchases can be tracked here.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Asset", "account_name": "Sales to Customers (Cash)", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Cost Of Goods Sold", "account_name": "Subcontractor", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": " An expense account to track the amount that you pay subcontractors who provide service to you.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Other Current Liability", "account_name": "TDS Payable", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Asset", "account_name": "TDS Receivable", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Transportation Expense", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An expense account to track the amount spent on transporting goods or providing services.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Bank", "account_name": "Bank Account", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Cash", "account_name": "Cash Account", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Credit Card", "account_name": "Credit Card Account", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Payment Clearing Account", "account_name": "Payment Clearing Account", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
        ]

        for account in account_info:
            if not Fin_Chart_Of_Account.objects.filter(Company = com,account_name=account['account_name']).exists():
                new_account = Fin_Chart_Of_Account(Company=account['company_id'],LoginDetails=account['Login_Id'],account_name=account['account_name'],account_type=account['account_type'],credit_card_no=account['credit_card_no'],sub_account=account['sub_account'],parent_account=account['parent_account'],bank_account_no=account['bank_account_no'],account_code=account['account_code'],description=account['description'],balance=account['balance'],balance_type=account['balance_type'],create_status=account['create_status'],status=account['status'],date=account['date'])
                new_account.save()

        #Adding Default Customer payment under company
        Fin_Company_Payment_Terms.objects.create(Company=com, term_name='Due on Receipt', days=0)
        Fin_Company_Payment_Terms.objects.create(Company=com, term_name='NET 30', days=30)
        Fin_Company_Payment_Terms.objects.create(Company=com, term_name='NET 60', days=60)  
        
        #sumayya-------- Adding default repeat every values for company

        Fin_CompanyRepeatEvery.objects.create(company=com, repeat_every = '3 Month', repeat_type='Month',duration = 3, days=90)
        Fin_CompanyRepeatEvery.objects.create(company=com, repeat_every = '6 Month', repeat_type='Month',duration = 6, days=180)
        Fin_CompanyRepeatEvery.objects.create(company=com, repeat_every = '1 Year', repeat_type='Year',duration=1,days=360)


        # Creating default transport entries with company information---aiswarya
        Fin_Eway_Transportation.objects.create(Name='Bus', Type='Road', Company=com)
        Fin_Eway_Transportation.objects.create(Name='Train', Type='Rail', Company=com)
        Fin_Eway_Transportation.objects.create(Name='Car', Type='Road', Company=com)

        
        Stock_Reason.objects.create(company=com,login_details=data,reason='Stock on fire')
        Stock_Reason.objects.create(company=com,login_details=data,reason='High demand of goods')
        Stock_Reason.objects.create(company=com,login_details=data,reason='Stock written off')
        Stock_Reason.objects.create(company=com,login_details=data,reason='Inventory Revaluation')


        print("add modules")
        return redirect('Fin_CompanyReg')
    return redirect('Fin_Modules',id)

def Fin_Edit_Modules(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        
        com = Fin_Company_Details.objects.get(Login_Id = s_id)
        allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
        module_request=Fin_Modules_List.objects.filter(company_id=com, status = 'pending')
           
        return render(request,'company/Fin_Edit_Modules.html',{'allmodules':allmodules,'com':com,'module_request': module_request,})
       
    else:
       return redirect('/') 
       
def Fin_Edit_Modules_Action(request): 
    if 's_id' in request.session:
        s_id = request.session['s_id']
        
        if request.method == 'POST':
            data = Fin_Login_Details.objects.get(id = s_id)
        
            com = Fin_Company_Details.objects.get(Login_Id = s_id)

            # -----ITEMS----

            Items = request.POST.get('c1')
            Price_List = request.POST.get('c2')
            Stock_Adjustment = request.POST.get('c3')


            # --------- CASH & BANK-----
            Cash_in_hand = request.POST.get('c4')
            Offline_Banking = request.POST.get('c5')
            Bank_Reconciliation = request.POST.get('c6')
            UPI = request.POST.get('c7')
            Bank_Holders = request.POST.get('c8')
            Cheque = request.POST.get('c9')
            Loan_Account = request.POST.get('c10')

            #  ------SALES MODULE -------
            Customers = request.POST.get('c11')
            Invoice  = request.POST.get('c12')
            Estimate = request.POST.get('c13')
            Sales_Order = request.POST.get('c14')
            Recurring_Invoice = request.POST.get('c15')
            Retainer_Invoice = request.POST.get('c16')
            Credit_Note = request.POST.get('c17')
            Payment_Received = request.POST.get('c18')
            Delivery_Challan = request.POST.get('c19')

            #  ---------PURCHASE MODULE--------- 
            Vendors = request.POST.get('c20') 
            Bills  = request.POST.get('c21')
            Recurring_Bills = request.POST.get('c22')
            Debit_Note = request.POST.get('c23')
            Purchase_Order = request.POST.get('c24')
            Expenses = request.POST.get('c25')
            Recurring_Expenses = request.POST.get('c26')
            Payment_Made = request.POST.get('c27')
            EWay_Bill = request.POST.get('c28')

            #  -------ACCOUNTS--------- 
            Chart_of_Accounts = request.POST.get('c29') 
            Manual_Journal = request.POST.get('c30')
            Reconcile  = request.POST.get('c36')


            # -------PAYROLL------- 
            Employees = request.POST.get('c31')
            Employees_Loan = request.POST.get('c32')
            Holiday = request.POST.get('c33') 
            Attendance = request.POST.get('c34')
            Salary_Details = request.POST.get('c35')

            modules = Fin_Modules_List(Items = Items,Price_List = Price_List,Stock_Adjustment = Stock_Adjustment,
                Cash_in_hand = Cash_in_hand,Offline_Banking = Offline_Banking,Bank_Reconciliation = Bank_Reconciliation ,
                UPI = UPI,Bank_Holders = Bank_Holders,Cheque = Cheque,Loan_Account = Loan_Account,
                Customers = Customers,Invoice = Invoice,Estimate = Estimate,Sales_Order = Sales_Order,
                Recurring_Invoice = Recurring_Invoice,Retainer_Invoice = Retainer_Invoice,Credit_Note = Credit_Note,
                Payment_Received = Payment_Received,Delivery_Challan = Delivery_Challan,
                Vendors = Vendors,Bills = Bills,Recurring_Bills = Recurring_Bills,Debit_Note = Debit_Note,
                Purchase_Order = Purchase_Order,Expenses = Expenses,Recurring_Expenses = Recurring_Expenses,
                Payment_Made = Payment_Made,EWay_Bill = EWay_Bill,
                Chart_of_Accounts = Chart_of_Accounts,Manual_Journal = Manual_Journal,Reconcile = Reconcile ,
                Employees = Employees,Employees_Loan = Employees_Loan,Holiday = Holiday,
                Attendance = Attendance,Salary_Details = Salary_Details,
                Login_Id = data,company_id = com,status = 'pending')
            
            modules.save()
            data1=Fin_Modules_List.objects.filter(company_id = com).update(update_action=1)

            if com.Registration_Type == 'self':
                noti = Fin_ANotification(Login_Id = data,Modules_List = modules,Title = "Module Updation",Discription = com.Company_name + " wants to update current Modules")
                noti.save()
            else:
                noti = Fin_DNotification(Distributor_id = com.Distributor_id,Login_Id = data,Modules_List = modules,Title = "Module Updation",Discription = com.Company_name + " wants to update current Modules")
                noti.save()   

            print("edit modules")
            return redirect('Fin_Company_Profile')
        return redirect('Fin_Edit_Modules')
       
    else:
       return redirect('/')   
    


def Fin_Company_Profile(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            terms = Fin_Payment_Terms.objects.all()
            
            payment_request=Fin_Payment_Terms_updation.objects.filter(Login_Id=com.Login_Id,status='New').exists()

            noti = Fin_CNotification.objects.filter(status = 'New',Company_id = com)
            n = len(noti)
            return render(request,'company/Fin_Company_Profile.html',{'allmodules':allmodules,'com':com,'data':data,'terms':terms,'noti':noti,'n':n,'payment_request':payment_request})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            return render(request,'company/Fin_Company_Profile.html',{'allmodules':allmodules,'com':com,'data':data})
        
    else:
       return redirect('/') 

    
def Fin_Staff_Req(request): 
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        com = Fin_Company_Details.objects.get(Login_Id = s_id)
        data1 = Fin_Staff_Details.objects.filter(company_id = com.id,Company_approval_status = "NULL")
        allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
        return render(request,'company/Fin_Staff_Req.html',{'com':com,'data':data,'allmodules':allmodules,'data1':data1})
    else:
       return redirect('/') 

def Fin_Staff_Req_Accept(request,id):
   data = Fin_Staff_Details.objects.get(id=id)
   data.Company_approval_status = 'Accept'
   data.save()
   return redirect('Fin_Staff_Req')

def Fin_Staff_Req_Reject(request,id):
   data = Fin_Staff_Details.objects.get(id=id)
   data.Login_Id.delete()
   data.delete()
   return redirect('Fin_Staff_Req')  

def Fin_Staff_delete(request,id):
   data = Fin_Staff_Details.objects.get(id=id)
   data.Login_Id.delete()
   data.delete()
   return redirect('Fin_All_Staff')  

def Fin_All_Staff(request): 
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        com = Fin_Company_Details.objects.get(Login_Id = s_id)
        data1 = Fin_Staff_Details.objects.filter(company_id = com.id,Company_approval_status = "Accept")
        allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
        return render(request,'company/Fin_All_Staff.html',{'com':com,'data':data,'allmodules':allmodules,'data1':data1})
    else:
       return redirect('/')  


def Fin_Change_payment_terms(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        
        if request.method == 'POST':
            data = Fin_Login_Details.objects.get(id = s_id)
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            pt = request.POST['payment_term']

            pay = Fin_Payment_Terms.objects.get(id=pt)

            data1 = Fin_Payment_Terms_updation(Login_Id = data,Payment_Term = pay)
            data1.save()

            if com.Registration_Type == 'self':
                noti = Fin_ANotification(Login_Id = data,PaymentTerms_updation = data1,Title = "Change Payment Terms",Discription = com.Company_name + " wants to subscribe a new plan")
                noti.save()
            else:
                noti = Fin_DNotification(Distributor_id = com.Distributor_id,Login_Id = data,PaymentTerms_updation = data1,Title = "Change Payment Terms",Discription = com.Company_name + " wants to subscribe a new plan")
                noti.save()      


        
            return redirect('Fin_Company_Profile')
    else:
       return redirect('/') 
    
def Fin_Wrong(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
           com = Fin_Distributors_Details.objects.get(Login_Id = s_id)     
        terms = Fin_Payment_Terms.objects.all()
        context= {
            'com':com,
            'terms':terms
        }
        return render(request,"company/Fin_Wrong.html",context)    
    else:
       return redirect('/') 
    
def Fin_Wrong_Action(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        
        if request.method == 'POST':
            data = Fin_Login_Details.objects.get(id = s_id)

            if data.User_Type == "Company":
                com = Fin_Company_Details.objects.get(Login_Id = s_id)
                pt = request.POST['payment_term']

                pay = Fin_Payment_Terms.objects.get(id=pt)

                data1 = Fin_Payment_Terms_updation(Login_Id = data,Payment_Term = pay)
                data1.save()

                if com.Registration_Type == 'self':
                    noti = Fin_ANotification(Login_Id = data,PaymentTerms_updation = data1,Title = "Change Payment Terms",Discription = com.Company_name + " is change Payment Terms")
                    noti.save()
                else:
                    noti = Fin_DNotification(Distributor_id = com.Distributor_id,Login_Id = data,PaymentTerms_updation = data1,Title = "Change Payment Terms",Discription = com.Company_name + " is change Payment Terms")
                    noti.save()    


            
                return redirect('Fin_CompanyReg')
            else:
                com = Fin_Distributors_Details.objects.get(Login_Id = s_id)
                pt = request.POST['payment_term']

                pay = Fin_Payment_Terms.objects.get(id=pt)

                data1 = Fin_Payment_Terms_updation(Login_Id = data,Payment_Term = pay)
                data1.save()

                noti = Fin_ANotification(Login_Id = data,PaymentTerms_updation = data1,Title = "Change Payment Terms",Discription = com.Login_Id.First_name + com.Login_Id.Last_name + " is change Payment Terms")
                noti.save()

                return redirect('Fin_DistributorReg')



    else:
       return redirect('/')  

def Fin_Edit_Company_profile(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        com = Fin_Company_Details.objects.get(Login_Id = s_id)
        noti = Fin_CNotification.objects.filter(status = 'New',Company_id = com)
        n = len(noti)

        context ={
            'com':com,
            'data':data,
            'n':n,
            'noti':noti


        }

        return render(request,"company/Fin_Edit_Company_profile.html",context)    
    else:
       return redirect('/') 
    

def Fin_Edit_Company_profile_Action(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        com = Fin_Company_Details.objects.get(Login_Id = s_id)
        if request.method == 'POST':
            com.Login_Id.First_name = request.POST['first_name']
            com.Login_Id.Last_name = request.POST['last_name']
            com.Email = request.POST['email']
            com.Contact = request.POST['contact']
            com.Company_name = request.POST['cname']
            com.Address = request.POST['caddress']
            com.City = request.POST['city']
            com.State = request.POST['state']
            com.Pincode = request.POST['pincode']
            com.Business_name = request.POST['bname']
            com.Pan_NO = request.POST['pannum']
            com.GST_Type = request.POST.get('gsttype')
            com.GST_NO = request.POST.get('gstnum')
            com.Industry = request.POST['industry']
            com.Company_Type = request.POST['ctype']
            com.Image = request.FILES.get('img')
            
            gst_type=request.POST.get('gsttype')
            gst_no=request.POST.get('gstnum')
            gst=['unregistered Business','Overseas','Consumer']
            if gst_type in gst:
                com.Login_Id.save()
                com.save()
                messages.success(request,'Profile Updated')
                return redirect('Fin_Company_Profile')
            else:
                if gst_no == '':

                    messages.error(request,'GST number cannot be empty,')
                    return redirect('Fin_Edit_Company_profile')
                else:
                    com.Login_Id.save()
                    com.save()
                    messages.success(request,'Profile Updated')
                    return redirect('Fin_Company_Profile')

           
        return redirect('Fin_Edit_Company_profile')     
    else:
       return redirect('/') 
    
def Fin_Edit_Staff_profile(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        com = Fin_Staff_Details.objects.get(Login_Id = s_id)

        context ={
            'com':com
        }

        return render(request,"company/Fin_Edit_Staff_profile.html",context)    
    else:
       return redirect('/')    
    
def Fin_Edit_Staff_profile_Action(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        com = Fin_Staff_Details.objects.get(Login_Id = s_id)
        if request.method == 'POST':
            com.Login_Id.First_name = request.POST['first_name']
            com.Login_Id.Last_name = request.POST['last_name']
            com.Email = request.POST['email']
            com.contact = request.POST['contact']
            
            com.img = request.FILES.get('img')
            

            com.Login_Id.save()
            com.save()

            return redirect('Fin_Company_Profile')
        return redirect('Fin_Edit_Staff_profile')     
    else:
       return redirect('/')     
      
    
# ---------------------------end company------------------------------------     


# ------------------shemeem-----Items&ChartOfAccounts-----------------------

# Items
def Fin_items(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            items = Fin_Items.objects.filter(Company = com)
            return render(request,'company/Fin_Items.html',{'allmodules':allmodules,'com':com,'data':data,'items':items})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            items = Fin_Items.objects.filter(Company = com.company_id)
            return render(request,'company/Fin_Items.html',{'allmodules':allmodules,'com':com,'data':data,'items':items})
    else:
       return redirect('/')

def Fin_createItem(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            units = Fin_Units.objects.filter(Company = com)
            acc = Fin_Chart_Of_Account.objects.filter(Q(account_type='Expense') | Q(account_type='Other Expense') | Q(account_type='Cost Of Goods Sold'), Company=com).order_by('account_name')
            return render(request,'company/Fin_Add_Item.html',{'allmodules':allmodules,'com':com,'data':data,'units':units, 'accounts':acc})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            units = Fin_Units.objects.filter(Company = com.company_id)
            acc = Fin_Chart_Of_Account.objects.filter(Q(account_type='Expense') | Q(account_type='Other Expense') | Q(account_type='Cost Of Goods Sold'), Company=com.company_id).order_by('account_name')
            return render(request,'company/Fin_Add_Item.html',{'allmodules':allmodules,'com':com,'data':data,'units':units, 'accounts':acc})
    else:
       return redirect('/')

def Fin_createNewItem(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        if request.method == 'POST':
            name = request.POST['name']
            type = request.POST['type']
            unit = request.POST.get('unit')
            hsn = request.POST['hsn']
            tax = request.POST['taxref']
            gstTax = 0 if tax == 'non taxable' else request.POST['intra_st']
            igstTax = 0 if tax == 'non taxable' else request.POST['inter_st']
            purPrice = request.POST['pcost']
            purAccount = None if not 'pur_account' in request.POST or request.POST['pur_account'] == "" else request.POST['pur_account']
            purDesc = request.POST['pur_desc']
            salePrice = request.POST['salesprice']
            saleAccount = None if not 'sale_account' in request.POST or request.POST['sale_account'] == "" else request.POST['sale_account']
            saleDesc = request.POST['sale_desc']
            inventory = request.POST.get('invacc')
            stock = 0 if request.POST.get('stock') == "" else request.POST.get('stock')
            stockUnitRate = 0 if request.POST.get('stock_rate') == "" else request.POST.get('stock_rate')
            minStock = request.POST['min_stock']
            createdDate = date.today()
            
            #save item and transaction if item or hsn doesn't exists already
            if Fin_Items.objects.filter(Company=com, name__iexact=name).exists():
                res = f'<script>alert("{name} already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)
            elif Fin_Items.objects.filter(Company = com, hsn__iexact = hsn).exists():
                res = f'<script>alert("HSN - {hsn} already exists, try another.!");window.history.back();</script>'
                return HttpResponse(res)
            else:
                item = Fin_Items(
                    Company = com,
                    LoginDetails = data,
                    name = name,
                    item_type = type,
                    unit = unit,
                    hsn = hsn,
                    tax_reference = tax,
                    intra_state_tax = gstTax,
                    inter_state_tax = igstTax,
                    sales_account = saleAccount,
                    selling_price = salePrice,
                    sales_description = saleDesc,
                    purchase_account = purAccount,
                    purchase_price = purPrice,
                    purchase_description = purDesc,
                    item_created = createdDate,
                    min_stock = minStock,
                    inventory_account = inventory,
                    opening_stock = stock,
                    current_stock = stock,
                    stock_in = 0,
                    stock_out = 0,
                    stock_unit_rate = stockUnitRate,
                    status = 'Active'
                )
                item.save()

                #save transaction

                Fin_Items_Transaction_History.objects.create(
                    Company = com,
                    LoginDetails = data,
                    item = item,
                    action = 'Created'
                )
                
                return redirect(Fin_items)

        return redirect(Fin_createItem)
    else:
       return redirect('/')

def Fin_viewItem(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            item = Fin_Items.objects.get(id = id)
            hist = Fin_Items_Transaction_History.objects.filter(Company = com, item = item).last()
            cmt = Fin_Items_Comments.objects.filter(item = item)
            context = {'allmodules':allmodules,'com':com,'data':data,'item':item, 'history': hist,'comments':cmt}
            return render(request,'company/Fin_View_Item.html',context)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            item = Fin_Items.objects.get(id = id)
            hist = Fin_Items_Transaction_History.objects.filter(Company = com.company_id, item = item).last()
            cmt = Fin_Items_Comments.objects.filter(item = item)
            context = {'allmodules':allmodules,'com':com,'data':data,'item':item, 'history': hist,'comments':cmt}
            return render(request,'company/Fin_View_Item.html',context)
    else:
       return redirect('/')
    
def Fin_saveItemUnit(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        if request.method == "POST":
            name = request.POST['name'].upper()

            if not Fin_Units.objects.filter(Company = com, name__iexact = name).exists():
                unit = Fin_Units(
                    Company = com,
                    name = name
                )
                unit.save()
                return JsonResponse({'status':True})
            else:
                return JsonResponse({'status':False, 'message':'Unit already exists.!'})

def Fin_getItemUnits(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        list= []
        option_objects = Fin_Units.objects.filter(Company = com)

        for item in option_objects:
            itemUnitDict = {
                'name': item.name,
            }
            list.append(itemUnitDict)

        return JsonResponse({'units':list},safe=False)
    
def Fin_createNewAccountFromItems(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        if request.method == 'POST':
            name = request.POST['account_name']
            type = request.POST['account_type']
            subAcc = True if request.POST['subAccountCheckBox'] == 'true' else False
            parentAcc = request.POST['parent_account'] if subAcc == True else None
            accCode = request.POST['account_code']
            bankAccNum = None
            desc = request.POST['description']
            
            createdDate = date.today()
            
            #save account and transaction if account doesn't exists already
            if Fin_Chart_Of_Account.objects.filter(Company=com, account_name__iexact=name).exists():
                res = f'<script>alert("{name} already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)
            else:
                account = Fin_Chart_Of_Account(
                    Company = com,
                    LoginDetails = data,
                    account_type = type,
                    account_name = name,
                    account_code = accCode,
                    description = desc,
                    balance = 0.0,
                    balance_type = None,
                    credit_card_no = None,
                    sub_account = subAcc,
                    parent_account = parentAcc,
                    bank_account_no = bankAccNum,
                    date = createdDate,
                    create_status = 'added',
                    status = 'active'
                )
                account.save()

                #save transaction

                Fin_ChartOfAccount_History.objects.create(
                    Company = com,
                    LoginDetails = data,
                    account = account,
                    action = 'Created'
                )
                
                list= []
                account_objects = Fin_Chart_Of_Account.objects.filter(Q(account_type='Expense') | Q(account_type='Other Expense'), Company=com).order_by('account_name')

                for account in account_objects:
                    accounts = {
                        'name': account.account_name,
                    }
                    list.append(accounts)

                return JsonResponse({'status':True,'accounts':list},safe=False)

        return JsonResponse({'status':False})
    else:
       return redirect('/')
    
def Fin_changeItemStatus(request,id,status):
    if 's_id' in request.session:
        
        item = Fin_Items.objects.get(id = id)
        item.status = status
        item.save()
        return redirect(Fin_viewItem, id)

def Fin_editItem(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        item = Fin_Items.objects.get(id = id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            units = Fin_Units.objects.filter(Company = com)
            acc = Fin_Chart_Of_Account.objects.filter(Q(account_type='Expense') | Q(account_type='Other Expense') | Q(account_type='Cost Of Goods Sold'), Company=com).order_by('account_name')
            return render(request,'company/Fin_Edit_Item.html',{'allmodules':allmodules,'com':com,'data':data,'units':units, 'accounts':acc, 'item':item})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            units = Fin_Units.objects.filter(Company = com.company_id)
            acc = Fin_Chart_Of_Account.objects.filter(Q(account_type='Expense') | Q(account_type='Other Expense') | Q(account_type='Cost Of Goods Sold'), Company=com.company_id).order_by('account_name')
            return render(request,'company/Fin_Edit_Item.html',{'allmodules':allmodules,'com':com,'data':data,'units':units, 'accounts':acc, 'item':item})
    else:
       return redirect('/')
    

def Fin_updateItem(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        item = Fin_Items.objects.get(id = id)
        if request.method == 'POST':
            name = request.POST['name']
            type = request.POST['type']
            unit = request.POST.get('unit')
            hsn = int(request.POST['hsn'])
            tax = request.POST['taxref']
            gstTax = 0 if tax == 'non taxable' else request.POST['intra_st']
            igstTax = 0 if tax == 'non taxable' else request.POST['inter_st']
            purPrice = request.POST['pcost']
            purAccount =  None if not 'pur_account' in request.POST or request.POST['pur_account'] == "" else request.POST['pur_account']
            purDesc = request.POST['pur_desc']
            salePrice = request.POST['salesprice']
            saleAccount = None if not 'sale_account' in request.POST or request.POST['sale_account'] == "" else request.POST['sale_account']
            saleDesc = request.POST['sale_desc']
            inventory = request.POST.get('invacc')
            stock = item.opening_stock if request.POST.get('stock') == "" else request.POST.get('stock')
            stockUnitRate = 0 if request.POST.get('stock_rate') == "" else request.POST.get('stock_rate')
            minStock = request.POST['min_stock']
            createdDate = date.today()

            oldOpen = int(item.opening_stock)
            newOpen = int(stock)
            diff = abs(oldOpen - newOpen)

            
            #save item and transaction if item or hsn doesn't exists already
            if item.name != name and Fin_Items.objects.filter(Company=com, name__iexact=name).exists():
                res = f'<script>alert("{name} already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)
            elif item.hsn != hsn and Fin_Items.objects.filter(Company = com, hsn__iexact = hsn).exists():
                res = f'<script>alert("HSN - {hsn} already exists, try another.!");window.history.back();</script>'
                return HttpResponse(res)
            else:
                item.Company = com
                item.LoginDetails = data
                item.name = name
                item.item_type = type
                item.unit = unit
                item.hsn = hsn
                item.tax_reference = tax
                item.intra_state_tax = gstTax
                item.inter_state_tax = igstTax
                item.sales_account = saleAccount
                item.selling_price = salePrice
                item.sales_description = saleDesc
                item.purchase_account = purAccount
                item.purchase_price = purPrice
                item.purchase_description = purDesc
                item.item_created = createdDate
                item.min_stock = minStock
                item.inventory_account = inventory
                
                if item.opening_stock != int(stock) and oldOpen > newOpen:
                    item.current_stock -= diff
                elif item.opening_stock != int(stock) and oldOpen < newOpen:
                    item.current_stock += diff
                
                item.opening_stock = stock
                item.stock_unit_rate = stockUnitRate

                item.save()

                #save transaction

                Fin_Items_Transaction_History.objects.create(
                    Company = com,
                    LoginDetails = data,
                    item = item,
                    action = 'Edited'
                )
                
                return redirect(Fin_viewItem, item.id)

        return redirect(Fin_editItem, item.id)
    else:
       return redirect('/')

def Fin_deleteItem(request, id):
    if 's_id' in request.session:
        item = Fin_Items.objects.get(id = id)
        #check whether any transaction are completed for the item(sales,purchase,estimate,bill etc.), if so, restrict deletion.

        item.delete()
        return redirect(Fin_items)

def Fin_itemHistory(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        itm = Fin_Items.objects.get(id = id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            his = Fin_Items_Transaction_History.objects.filter(Company = com , item = itm)
            return render(request,'company/Fin_Item_History.html',{'allmodules':allmodules,'com':com,'data':data,'history':his, 'item':itm})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            his = Fin_Items_Transaction_History.objects.filter(Company = com.company_id, item = itm)
            return render(request,'company/Fin_Item_History.html',{'allmodules':allmodules,'com':com,'data':data,'history':his, 'item':itm})
    else:
       return redirect('/')

def Fin_itemTransactionPdf(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
        
        item = Fin_Items.objects.get(id = id)
        stock = int(item.current_stock)
        rate = float(item.stock_unit_rate)
        stockValue = float(stock * rate)
    
        context = {'item': item, 'stockValue':stockValue}
        
        template_path = 'company/Fin_Item_Transaction_Pdf.html'
        fname = 'Item_transactions_'+item.name
        # return render(request, 'company/Fin_Item_Transaction_Pdf.html',context)
        # Create a Django response object, and specify content_type as pdftemp_
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] =f'attachment; filename = {fname}.pdf'
        # find the template and render it.
        template = get_template(template_path)
        html = template.render(context)

        # create a pdf
        pisa_status = pisa.CreatePDF(
        html, dest=response)
        # if error then show some funny view
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
    else:
        return redirect('/')
    
def Fin_shareItemTransactionsToEmail(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        item = Fin_Items.objects.get(id = id)
        try:
            if request.method == 'POST':
                emails_string = request.POST['email_ids']

                # Split the string by commas and remove any leading or trailing whitespace
                emails_list = [email.strip() for email in emails_string.split(',')]
                email_message = request.POST['email_message']
                # print(emails_list)
            
                stock = int(item.current_stock)
                rate = float(item.stock_unit_rate)
                stockValue = float(stock * rate)
            
                context = {'item': item, 'stockValue':stockValue}
                template_path = 'company/Fin_Item_Transaction_Pdf.html'
                template = get_template(template_path)

                html  = template.render(context)
                result = BytesIO()
                pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
                pdf = result.getvalue()
                filename = f'Item_transactions-{item.name}.pdf'
                subject = f"Item_transactions_{item.name}"
                email = EmailMessage(subject, f"Hi,\nPlease find the attached Transaction details - ITEM-{item.name}. \n{email_message}\n\n--\nRegards,\n{com.Company_name}\n{com.Address}\n{com.State} - {com.Country}\n{com.Contact}", from_email=settings.EMAIL_HOST_USER, to=emails_list)
                email.attach(filename, pdf, "application/pdf")
                email.send(fail_silently=False)

                messages.success(request, 'Bill has been shared via email successfully..!')
                return redirect(Fin_viewItem,id)
        except Exception as e:
            print(e)
            messages.error(request, f'{e}')
            return redirect(Fin_viewItem, id)
        
def Fin_addItemComment(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        itm = Fin_Items.objects.get(id = id)
        if request.method == "POST":
            cmt = request.POST['comment'].strip()

            Fin_Items_Comments.objects.create(Company = com, item = itm, comments = cmt)
            return redirect(Fin_viewItem, id)
        return redirect(Fin_viewItem, id)
    return redirect('/')

def Fin_deleteItemComment(request,id):
    if 's_id' in request.session:
        cmt = Fin_Items_Comments.objects.get(id = id)
        itemId = cmt.item.id
        cmt.delete()
        return redirect(Fin_viewItem, itemId)


# Chart of accounts

def Fin_chartOfAccounts(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            acc = Fin_Chart_Of_Account.objects.filter(Company = com)
            return render(request,'company/Fin_ChartOfAccounts.html',{'allmodules':allmodules,'com':com,'data':data,'accounts':acc})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            acc = Fin_Chart_Of_Account.objects.filter(Company = com.company_id)
            return render(request,'company/Fin_ChartOfAccounts.html',{'allmodules':allmodules,'com':com,'data':data,'accounts':acc})
    else:
       return redirect('/')

def Fin_addAccount(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            return render(request,'company/Fin_Add_Account.html',{'allmodules':allmodules,'com':com,'data':data})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            return render(request,'company/Fin_Add_Account.html',{'allmodules':allmodules,'com':com,'data':data})
    else:
       return redirect('/')
    
def Fin_checkAccounts(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        if Fin_Chart_Of_Account.objects.filter(Company = com, account_type = request.GET['type']).exists():
            list= []
            account_objects = Fin_Chart_Of_Account.objects.filter(Company = com, account_type = request.GET['type'])

            for account in account_objects:
                accounts = {
                    'name': account.account_name,
                }
                list.append(accounts)

            return JsonResponse({'status':True,'accounts':list},safe=False)
        else:
            return JsonResponse({'status':False})

def Fin_createAccount(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        if request.method == 'POST':
            name = request.POST['account_name']
            type = request.POST['account_type']
            subAcc = True if 'subAccountCheckBox' in request.POST else False
            parentAcc = request.POST['parent_account'] if 'subAccountCheckBox' in request.POST else None
            accCode = request.POST['account_code']
            bankAccNum = None if request.POST['account_number'] == "" else request.POST['account_number']
            desc = request.POST['description']
            
            createdDate = date.today()
            
            #save account and transaction if account doesn't exists already
            if Fin_Chart_Of_Account.objects.filter(Company=com, account_name__iexact=name).exists():
                res = f'<script>alert("{name} already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)
            else:
                account = Fin_Chart_Of_Account(
                    Company = com,
                    LoginDetails = data,
                    account_type = type,
                    account_name = name,
                    account_code = accCode,
                    description = desc,
                    balance = 0.0,
                    balance_type = None,
                    credit_card_no = None,
                    sub_account = subAcc,
                    parent_account = parentAcc,
                    bank_account_no = bankAccNum,
                    date = createdDate,
                    create_status = 'added',
                    status = 'active'
                )
                account.save()

                #save transaction

                Fin_ChartOfAccount_History.objects.create(
                    Company = com,
                    LoginDetails = data,
                    account = account,
                    action = 'Created'
                )
                
                return redirect(Fin_chartOfAccounts)

        return redirect(Fin_createAccount)
    else:
       return redirect('/')

def Fin_accountOverview(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        acc = Fin_Chart_Of_Account.objects.get(id = id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            hist = Fin_ChartOfAccount_History.objects.filter(Company = com, account = acc).last()
            return render(request,'company/Fin_Account_Overview.html',{'allmodules':allmodules,'com':com,'data':data, 'account':acc, 'history':hist})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            hist = Fin_ChartOfAccount_History.objects.filter(Company = com.company_id, account = acc).last()
            return render(request,'company/Fin_Account_Overview.html',{'allmodules':allmodules,'com':com,'data':data, 'account':acc, 'history':hist})
    else:
       return redirect('/')
    
def Fin_changeAccountStatus(request,id,status):
    if 's_id' in request.session:
        
        acc = Fin_Chart_Of_Account.objects.get(id = id)
        acc.status = status
        acc.save()
        return redirect(Fin_accountOverview, id)
    
def Fin_accountTransactionPdf(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
        
        acc = Fin_Chart_Of_Account.objects.get(id = id)
    
        context = {'account': acc}
        
        template_path = 'company/Fin_Account_Transaction_Pdf.html'
        fname = 'Account_transactions_'+acc.account_name
        # return render(request, 'company/Fin_Account_Transaction_Pdf.html',context)
        # Create a Django response object, and specify content_type as pdftemp_
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] =f'attachment; filename = {fname}.pdf'
        # find the template and render it.
        template = get_template(template_path)
        html = template.render(context)

        # create a pdf
        pisa_status = pisa.CreatePDF(
        html, dest=response)
        # if error then show some funny view
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
    else:
        return redirect('/')

def Fin_shareAccountTransactionsToEmail(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        acc = Fin_Chart_Of_Account.objects.get(id = id)
        try:
            if request.method == 'POST':
                emails_string = request.POST['email_ids']

                # Split the string by commas and remove any leading or trailing whitespace
                emails_list = [email.strip() for email in emails_string.split(',')]
                email_message = request.POST['email_message']
                # print(emails_list)
            
                context = {'account': acc}
                template_path = 'company/Fin_Account_Transaction_Pdf.html'
                template = get_template(template_path)

                html  = template.render(context)
                result = BytesIO()
                pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
                pdf = result.getvalue()
                filename = f'Account_transactions-{acc.account_name}.pdf'
                subject = f"Account_transactions_{acc.account_name}"
                email = EmailMessage(subject, f"Hi,\nPlease find the attached Transaction details - ACCOUNT-{acc.account_name}. \n{email_message}\n\n--\nRegards,\n{com.Company_name}\n{com.Address}\n{com.State} - {com.Country}\n{com.Contact}", from_email=settings.EMAIL_HOST_USER, to=emails_list)
                email.attach(filename, pdf, "application/pdf")
                email.send(fail_silently=False)

                messages.success(request, 'Bill has been shared via email successfully..!')
                return redirect(Fin_accountOverview,id)
        except Exception as e:
            print(e)
            messages.error(request, f'{e}')
            return redirect(Fin_accountOverview, id)

def Fin_deleteAccount(request, id):
    if 's_id' in request.session:
        acc = Fin_Chart_Of_Account.objects.get( id = id)
        acc.delete()
        return redirect(Fin_chartOfAccounts)

def Fin_editAccount(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            acc = Fin_Chart_Of_Account.objects.get(id = id)
            return render(request,'company/Fin_Edit_Account.html',{'allmodules':allmodules,'com':com,'data':data, 'account':acc})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            acc = Fin_Chart_Of_Account.objects.get(id = id)
            return render(request,'company/Fin_Edit_Account.html',{'allmodules':allmodules,'com':com,'data':data, 'account':acc})
    else:
       return redirect('/')

def Fin_updateAccount(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        acc = Fin_Chart_Of_Account.objects.get(id = id)
        if request.method == 'POST':
            name = request.POST['account_name']
            subAcc = True if 'subAccountCheckBox' in request.POST else False
            parentAcc = request.POST['parent_account'] if 'subAccountCheckBox' in request.POST else None
            accCode = request.POST['account_code']
            bankAccNum = None if request.POST['account_number'] == "" else request.POST['account_number']
            desc = request.POST['description']
            
            #save account and transaction if account doesn't exists already
            if acc.account_name != name and Fin_Chart_Of_Account.objects.filter(Company=com, account_name__iexact=name).exists():
                res = f'<script>alert("{name} already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)
            else:
                acc.account_name = name
                acc.account_code = accCode
                acc.description = desc
                acc.sub_account = subAcc
                acc.parent_account = parentAcc
                acc.bank_account_no = bankAccNum
                acc.save()

                #save transaction
                if acc.create_status == 'added':
                    Fin_ChartOfAccount_History.objects.create(
                        Company = com,
                        LoginDetails = data,
                        account = acc,
                        action = 'Edited'
                    )
                
                return redirect(Fin_accountOverview, id)

        return redirect(Fin_editAccount, id)
    else:
       return redirect('/')
    
def Fin_accountHistory(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        acc = Fin_Chart_Of_Account.objects.get(id = id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            his = Fin_ChartOfAccount_History.objects.filter(Company = com , account = acc)
            return render(request,'company/Fin_Account_History.html',{'allmodules':allmodules,'com':com,'data':data,'history':his, 'account':acc})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            his = Fin_ChartOfAccount_History.objects.filter(Company = com.company_id, account = acc)
            return render(request,'company/Fin_Account_History.html',{'allmodules':allmodules,'com':com,'data':data,'history':his, 'account':acc})
    else:
       return redirect('/')
       
#End

def Fin_bankholder(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        try:
            data = Fin_Login_Details.objects.get(id=s_id)
            if data.User_Type == "Company":
                com = Fin_Company_Details.objects.get(Login_Id=s_id)
                allmodules = Fin_Modules_List.objects.get(Login_Id=s_id,status='New')
                bank_holders = Fin_BankHolder.objects.filter(Company=com)
                comments = Fin_BankHolderComment.objects.filter(Company=com)
                history = Fin_BankHolderHistory.objects.filter(Company=com)
                banking_details = Fin_Banking.objects.filter(company=com) 
                
            else:
                com = Fin_Staff_Details.objects.get(Login_Id=s_id)
                # com = staff_details.company_id 
                allmodules = Fin_Modules_List.objects.get(company_id=com.company_id, status='New')
                bank_holders = Fin_BankHolder.objects.filter(Company=com.company_id)
                comments = Fin_BankHolderComment.objects.filter(Company=com.company_id)
                history = Fin_BankHolderHistory.objects.filter(Company=com.company_id)
                banking_details = Fin_Banking.objects.filter(company=com.company_id) 
            
            sort_by = request.GET.get('sort_by', None)
            if sort_by == 'holder_name':
                bank_holders = bank_holders.order_by('Holder_name')
            elif sort_by == 'bank_name':
                bank_holders = bank_holders.order_by('Bank_name')

            context = {
                'com': com,
                'bank_holders': bank_holders,
                'comments': comments,
                'history': history,
                'sort_by': sort_by,
                'banking_details':banking_details,
                'allmodules':allmodules,
                'data':data,              
            }
            return render(request, 'company/Fin_Bankholders.html', context)
        except Fin_Login_Details.DoesNotExist:
            return redirect('/')
    else:
        return redirect('/')  


def Fin_addbank(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        try:
            data = Fin_Login_Details.objects.get(id=s_id)
            if data.User_Type == "Company":
                com = Fin_Company_Details.objects.get(Login_Id=data)
                allmodules = Fin_Modules_List.objects.get(Login_Id=s_id,status='New')
                bank_names = Fin_Banking.objects.filter(company=com).values_list('bank_name', flat=True).distinct()
                bank_holders = Fin_BankHolder.objects.filter(Company=com)
                comments = Fin_BankHolderComment.objects.filter(Company=com)
                history = Fin_BankHolderHistory.objects.filter(Company=com)
                banking_details = Fin_Banking.objects.filter(company=com)
                bank_history = Fin_BankingHistory.objects.filter(company=com)
            else:
                com = Fin_Staff_Details.objects.get(Login_Id=data)
                # com = staff_details.company_id 
                allmodules = Fin_Modules_List.objects.get(company_id=com.company_id, status='New')
                bank_names = Fin_Banking.objects.filter(company=com.company_id).values_list('bank_name', flat=True).distinct()
                bank_holders = Fin_BankHolder.objects.filter(Company=com.company_id)
                comments = Fin_BankHolderComment.objects.filter(Company=com.company_id)
                history = Fin_BankHolderHistory.objects.filter(Company=com.company_id)
                banking_details = Fin_Banking.objects.filter(company=com.company_id)
                bank_history = Fin_BankingHistory.objects.filter(company=com.company_id)

           

            context = {
                'com': com,
                'bank_names': bank_names,
                'bank_holders':bank_holders,
                'comments':comments,
                'history':history,
                'banking_details':banking_details,
                'bank_history':bank_history,
                'LoginDetails': data,
                'allmodules':allmodules,
                'data':data,

            }
            return render(request, 'company/Fin_Createbankholder.html', context)
        except Fin_Login_Details.DoesNotExist:
            return redirect('/') 
    return redirect('Fin_bankholder')

def Fin_fetchaccountnumbers(request):
    try:
        if request.method == 'GET' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
            selected_bank = request.GET.get('bank_name', None)

            if 's_id' in request.session:
                s_id = request.session['s_id']
                try:
                    user_data = Fin_Login_Details.objects.get(id=s_id)

                    if user_data.User_Type == "Company":
                        company = Fin_Company_Details.objects.get(Login_Id=s_id)
                    else:
                        staff_details = Fin_Staff_Details.objects.get(Login_Id=s_id)
                        company = staff_details.company_id

                    if selected_bank:
                        account_numbers_queryset = Fin_Banking.objects.filter(bank_name=selected_bank, company=company)
                        account_numbers = [
                            {
                                'account_number': account.account_number,
                                'ifsc_code': account.ifsc_code,
                                'branch_name': account.branch_name
                            }
                            for account in account_numbers_queryset
                        ]
                        data = {'account_numbers': account_numbers}
                        return JsonResponse(data, safe=False)
                except Fin_Login_Details.DoesNotExist:
                    return JsonResponse({'error': 'User not found'}, status=404)
            else:
                return JsonResponse({'error': 'User not authenticated'}, status=401)

        return JsonResponse({}, status=400)
    except Exception as e:
        print(f"Error in Fin_fetchaccountnumbers: {str(e)}")
        return JsonResponse({'error': 'Internal Server Error'}, status=500)

def Fin_fetchallbanks(request):
    try:
        if 's_id' in request.session:
            s_id = request.session['s_id']
            user_data = Fin_Login_Details.objects.get(id=s_id)

            if user_data.User_Type == "Company":
                company = Fin_Company_Details.objects.get(Login_Id=s_id)
            else:
                staff_details = Fin_Staff_Details.objects.get(Login_Id=s_id)
                company = staff_details.company_id

            banks = Fin_Banking.objects.filter(company=company).values('bank_name')

            return JsonResponse({'banks': list(banks)})
        else:
            return JsonResponse({'error': 'User not authenticated'}, status=401)
    except Exception as e:
        print(f"Error in Fin_fetchallbanks: {str(e)}")
        return JsonResponse({'error': 'Internal Server Error'}, status=500)
    
def Fin_Bankaccountholder(request):
    selected_bank = None
    error_message_account = ""
    
    if 's_id' in request.session:
        s_id = request.session['s_id']
        try:
            data = Fin_Login_Details.objects.get(id=s_id)

            if data.User_Type == "Company":
                # Company case
                com = Fin_Company_Details.objects.get(Login_Id=data)
                allmodules = Fin_Modules_List.objects.get(Login_Id=s_id, status='New')
                account_holder = Fin_BankHolder.objects.filter(Company=com)
                bank_queryset = Fin_Banking.objects.filter(company=com)

            else:
                # Staff case
                com = Fin_Staff_Details.objects.get(Login_Id=data)
                allmodules = Fin_Modules_List.objects.get(company_id=com.company_id, status='New')
                account_holder = Fin_BankHolder.objects.filter(Company=com.company_id)
                bank_queryset = Fin_Banking.objects.filter(company=com.company_id)

            if request.method == "POST":
                try:
                    swift_code = request.POST['swiftCode']
                    name = request.POST['name']
                    alias = request.POST['alias']
                    phone_number = request.POST['phone_number']
                    email = request.POST['email']
                    account_type = request.POST['account_type']
                    mailing_name = request.POST['mailingName']
                    address = request.POST['address']
                    country = request.POST['country']
                    state = request.POST['state']
                    pin = request.POST['pin']
                    date = request.POST['date']
                    amount = request.POST['Opening']
                    pan_it_number = request.POST['pan_it_number']
                    registration_type = request.POST['registration_type']
                    gstin_un = request.POST['gstin_un']
                    types = request.POST['termof']
                    set_cheque_book_range = request.POST['set_cheque_book_range']
                    enable_cheque_printing = request.POST['enable_cheque_printing']
                    set_cheque_printing_configuration = request.POST['set_cheque_printing_configuration']
                    if 'bank_name' in request.POST:
                        selected_bank_name = request.POST['bank_name']
                        account_number = request.POST.get('accountNumber', '')
                        ifsc_code = request.POST.get('ifscCode', '')

                        if data.User_Type == "Company":
                            bank_queryset = Fin_Banking.objects.filter(
                                company=com,
                                bank_name=selected_bank_name,
                                account_number=account_number,
                                ifsc_code=ifsc_code
                            )

                            if not bank_queryset.exists():
                                selected_bank = Fin_Banking.objects.create(
                                    company=com,
                                    bank_name=selected_bank_name,
                                    branch_name=request.POST.get('branch_name', ''),
                                    ifsc_code=request.POST.get('ifscCode', ''),
                                    account_number=account_number
                                )
                            else:
                                for bank_instance in bank_queryset:
                                    bank_instance.branch_name = request.POST.get('branch_name', '')
                                    bank_instance.ifsc_code = request.POST.get('ifscCode', '')
                                    bank_instance.save()

                                selected_bank = bank_queryset.first()

                        else:  # This is for 'Staff' scenario
                            bank_queryset = Fin_Banking.objects.filter(
                                company=com.company_id,
                                bank_name=selected_bank_name,
                                account_number=account_number,
                                ifsc_code=ifsc_code
                            )

                            if not bank_queryset.exists():
                                selected_bank = Fin_Banking.objects.create(
                                    company=com.company_id,
                                    bank_name=selected_bank_name,
                                    branch_name=request.POST.get('branch_name', ''),
                                    ifsc_code=request.POST.get('ifscCode', ''),
                                    account_number=account_number
                                )
                            else:
                                for bank_instance in bank_queryset:
                                    bank_instance.branch_name = request.POST.get('branch_name', '')
                                    bank_instance.ifsc_code = request.POST.get('ifscCode', '')
                                    bank_instance.save()

                                selected_bank = bank_queryset.first()

                        if selected_bank is not None:
                            swift_code = request.POST.get('swiftCode', '')

                        if Fin_BankHolder.objects.filter(
                            Q(Account_number=selected_bank.account_number) |
                            Q(phone_number=phone_number) |
                            Q(Pan_it_number=pan_it_number) |
                            Q(Email=email),
                            Company=com if data.User_Type == "Company" else com.company_id
                        ).exists():
                            existing_holder = Fin_BankHolder.objects.filter(
                                Q(Account_number=selected_bank.account_number) |
                                Q(phone_number=phone_number) |
                                Q(Pan_it_number=pan_it_number) |
                                Q(Email=email),
                                Company=com if data.User_Type == "Company" else com.company_id
                            ).first()

                            error_messages = []

                            if existing_holder:
                                if existing_holder.Account_number == account_number:
                                    error_messages.append("Account number is already in use by another holder.")

                                if existing_holder.phone_number == phone_number:
                                    error_messages.append("Phone number is already in use by another holder.")

                                if existing_holder.Pan_it_number == pan_it_number:
                                    error_messages.append("PAN number is already in use by another holder.")

                                if existing_holder.Email == email:
                                    error_messages.append("Email is already in use by another holder.")

                                if registration_type in ['Regular', 'Composition']:
                                    gstin_un = request.POST.get('gstin_un', '')
                                    if Fin_BankHolder.objects.filter(Q(Gstin_un=gstin_un), Company=com if data.User_Type == "Company" else com.company_id).exists():
                                        error_messages.append("GST number is already in use by another holder.")

                            if error_messages:
                                print(f"Errors: {error_messages}")
                                context = {
                                    'bank': bank_queryset,
                                    'error_messages_account': error_messages,
                                    'com': com,
                                    'allmodules': allmodules,
                                    'data': data,
                                }
                                return render(request, 'company/Fin_Createbankholder.html', context)

                    account_holder = Fin_BankHolder(
                        LoginDetails=data,
                        Company=com if data.User_Type == "Company" else com.company_id,
                        Holder_name=name,
                        Alias=alias,
                        phone_number=phone_number,
                        Email=email,
                        Account_type=account_type,
                        Mailing_name=mailing_name,
                        Address=address,
                        Country=country,
                        State=state,
                        Pin=pin,
                        Date=date,
                        ArithmeticErrormount=amount,
                        Open_type=types,
                        Pan_it_number=pan_it_number,
                        Registration_type=registration_type,
                        Gstin_un=gstin_un,
                        Swift_code=swift_code,
                        Bank_name=selected_bank.bank_name,
                        Account_number=selected_bank.account_number,
                        Branch_name=selected_bank.branch_name,
                        Ifsc_code=selected_bank.ifsc_code,
                        Set_cheque_book_range=True if set_cheque_book_range == "Yes" else False,
                        Enable_cheque_printing=True if enable_cheque_printing == "Yes" else False,
                        Set_cheque_printing_configuration=True if set_cheque_printing_configuration == "Yes" else False,
                    )
                    account_holder.save()

                    account_holder.banking_details = selected_bank
                    account_holder.save()

                    Fin_BankHolderHistory.objects.create(
                        # Company=com,
                        Company=com if data.User_Type == "Company" else com.company_id,
                        LoginDetails=data,
                        Holder=account_holder,
                        date=timezone.now(),
                        action='Created'
                    )
                    return redirect('Fin_bankholder')

                except IntegrityError as e:
                    if 'unique constraint' in str(e).lower():
                        error_message_account = "Account details are already in use by another holder."
                    else:
                        error_message_account = "Error in creating bank holder."

                    print(f"Error: {error_message_account}")
                    return HttpResponse(f"Error: {error_message_account}")

            else:
                error_message = "Selected bank is None. Handle this case accordingly."
                print(f"Error: {error_message}")
                bank_queryset = Fin_Banking.objects.filter(company=com if data.User_Type == "Company" else com.company_id)
                context = {'bank': bank_queryset, 'error_message': error_message}
                return render(request, 'company/Fin_Createbankholder.html', context)

        except Fin_Login_Details.DoesNotExist:
            return redirect('/')

    return redirect('Fin_bankholder')

def Fin_AddBankinHolder(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        try:
            data = Fin_Login_Details.objects.get(id=s_id)

            if data.User_Type == "Company":
                com = Fin_Company_Details.objects.get(Login_Id=data)
                bank_queryset = Fin_Banking.objects.filter(company=com)
            else:
                staff_details = Fin_Staff_Details.objects.get(Login_Id=data)
                com = staff_details.company_id  
                bank_queryset = Fin_Banking.objects.filter(company=com)

            # bank_queryset = Fin_Banking.objects.filter(company=com)

            if request.method == 'POST':
                bank_name = request.POST.get('bank_name')
                ifsc_code = request.POST.get('ifsc_code')
                account_number = request.POST.get('account_number')
                branch_name = request.POST.get('branch_name')

                if not all([bank_name, ifsc_code, account_number, branch_name]):
                    return JsonResponse({'error_message': 'All fields are required'}, status=400)
                
                if bank_queryset.filter(account_number=account_number).exists():
                    return JsonResponse({'error_message': 'Account number already exists for this company'}, status=400)

                new_bank = Fin_Banking(
                    company=com,
                    bank_name=bank_name,
                    ifsc_code=ifsc_code,
                    account_number=account_number,
                    branch_name=branch_name,
                )
                new_bank.save()
                
                return JsonResponse({
                    'bank_name': new_bank.bank_name,
                })

        except Fin_Login_Details.DoesNotExist:
            return redirect('/')
    return JsonResponse({'error_message': 'Invalid request'}, status=400)
    
def Fin_Bankholderview(request, id):
    print(f"Requested ID: {id}")
    if 's_id' in request.session:
        s_id = request.session['s_id']
        try:
            data = Fin_Login_Details.objects.get(id=s_id)
            if data.User_Type == "Company":
                com = Fin_Company_Details.objects.get(Login_Id=data)
                allmodules = Fin_Modules_List.objects.get(Login_Id=s_id,status='New')
                account_holder = get_object_or_404(Fin_BankHolder, id=id)
                try:
                    banking_details = account_holder.banking_details
                except Fin_BankHolder.DoesNotExist:
                    banking_details = None
                last_history_entry = Fin_BankHolderHistory.objects.filter(Holder_id=account_holder).order_by('-date').first()
                comments = Fin_BankHolderComment.objects.filter(Holder=account_holder, Company=com)
            else:
                com = Fin_Staff_Details.objects.get(Login_Id=data)
                # com = staff_details.company_id
                allmodules = Fin_Modules_List.objects.get(company_id=com.company_id, status='New')
                account_holder = get_object_or_404(Fin_BankHolder, id=id)
                try:
                    banking_details = account_holder.banking_details
                except Fin_BankHolder.DoesNotExist:
                    banking_details = None
                last_history_entry = Fin_BankHolderHistory.objects.filter(Holder_id=account_holder).order_by('date').last()
                comments = Fin_BankHolderComment.objects.filter(Holder=account_holder, Company=com.company_id)


            context = {
                'account_holder': account_holder,
                'banking_details': banking_details,
                'com': com,
                'last_history_entry': last_history_entry,
                'comments': comments,
                'allmodules':allmodules,
                'data':data,
            }

            return render(request, 'company/Fin_Bankholderview.html', context)
        except Fin_Login_Details.DoesNotExist:
            return redirect('/')  
    return redirect('Fin_bankholder')


def Fin_activebankholder(request, id):
    account_holder = Fin_BankHolder.objects.get(id=id)
    account_holder.is_active = True
    account_holder.save()
    return redirect('Fin_Bankholderview', id=id)


def Fin_inactivatebankaccount(request, id):
    account_holder= Fin_BankHolder.objects.get(id=id)
    account_holder.is_active = False
    account_holder.save()
    return redirect('Fin_Bankholderview', id=id)

def Fin_Editbankholder(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        try:
            data = Fin_Login_Details.objects.get(id=s_id)
            if data.User_Type == "Company":
                com = Fin_Company_Details.objects.get(Login_Id=s_id)
                allmodules = Fin_Modules_List.objects.get(Login_Id=s_id, status='New')
                account_holder = get_object_or_404(Fin_BankHolder, id=id)
                banking_details = account_holder.banking_details  
            else:
                com = Fin_Staff_Details.objects.get(Login_Id=s_id)
                allmodules = Fin_Modules_List.objects.get(company_id=com.company_id, status='New')
                account_holder = get_object_or_404(Fin_BankHolder, id=id)
                banking_details = account_holder.banking_details  

            context = {
                'com': com,
                'account_holder': account_holder,
                'banking_details': banking_details,
                'allmodules': allmodules,
                'data': data,
            }
            return render(request, 'company/Fin_Editbankholder.html', context)
        except Fin_Login_Details.DoesNotExist:
            return redirect('/') 
    return redirect('Fin_bankholder')



def Fin_Editholder(request, id):
    selected_bank = None
    error_message_phone = ""
    error_message_email = ""
    error_message_account = ""
    e = None

    if 's_id' in request.session:
        s_id = request.session['s_id']
        try:
            data = Fin_Login_Details.objects.get(id=s_id)
            if data.User_Type == "Company":
                com = Fin_Company_Details.objects.get(Login_Id=s_id)
                allmodules = Fin_Modules_List.objects.get(Login_Id=s_id, status='New')
                account_holder = get_object_or_404(Fin_BankHolder, id=id, Company=com)

            else:
                com = Fin_Staff_Details.objects.get(Login_Id=s_id)
                allmodules = Fin_Modules_List.objects.get(company_id=com.company_id, status='New')
                account_holder = get_object_or_404(Fin_BankHolder, id=id, Company=com.company_id)
            
            if request.method == "POST":
                try:
                    name = request.POST.get('name')
                    alias = request.POST.get('alias')
                    phone_number = request.POST.get('phone_number')
                    email = request.POST.get('email')
                    account_type = request.POST.get('account_type')
                    mailing_name = request.POST.get('mailingName')
                    address = request.POST.get('address')
                    country = request.POST.get('country')
                    state = request.POST.get('state')
                    pin = request.POST.get('pin')
                    date_str = request.POST.get('date')
                    amount = request.POST.get('Opening')
                    types = request.POST.get('termof')
                    pan_it_number = request.POST.get('pan_it_number')
                    registration_type = request.POST.get('registration_type')
                    gstin_un = request.POST.get('gstin_un')
                    account_number = request.POST.get('accountNumber')
                    ifsc_code = request.POST.get('ifscCode')
                    swift_code = request.POST.get('swiftCode')
                    bank_name = request.POST.get('bank_name')
                    branch_name = request.POST.get('branch_name')
                    set_cheque_book_range = request.POST.get('set_cheque_book_range')
                    enable_cheque_printing = request.POST.get('enable_cheque_printing')
                    set_cheque_printing_configuration = request.POST.get('set_cheque_printing_configuration')

                    date = datetime.strptime(date_str, '%Y-%m-%d').date()

                    account_holder.Holder_name = name
                    account_holder.Alias = alias
                    account_holder.phone_number = phone_number
                    account_holder.Email = email
                    account_holder.Account_type = account_type
                    account_holder.Account_number = account_number
                    account_holder.Ifsc_code = ifsc_code
                    account_holder.Swift_code = swift_code
                    account_holder.Bank_name = bank_name
                    account_holder.Branch_name = branch_name
                    account_holder.Mailing_name = mailing_name
                    account_holder.Address = address
                    account_holder.Country = country
                    account_holder.State = state
                    account_holder.Pin = pin
                    account_holder.Date = date
                    account_holder.ArithmeticErrormount = amount
                    account_holder.Open_type = types
                    account_holder.Pan_it_number = pan_it_number
                    account_holder.Registration_type = registration_type
                    account_holder.Gstin_un = gstin_un
                    account_holder.Set_cheque_book_range = True if set_cheque_book_range == "Yes" else False
                    account_holder.Enable_cheque_printing = True if enable_cheque_printing == "Yes" else False
                    account_holder.Set_cheque_printing_configuration = True if set_cheque_printing_configuration == "Yes" else False

                    if 'bank_name' in request.POST:
                        selected_bank_name = request.POST['bank_name']
                        account_number = request.POST.get('accountNumber', '')
                        bank_queryset = Fin_Banking.objects.filter(bank_name=selected_bank_name, account_number=account_number, company=com if data.User_Type == "Company" else com.company_id)

                        if not bank_queryset.exists():
                            selected_bank = Fin_Banking.objects.create(
                                company=com if data.User_Type == "Company" else com.company_id,
                                bank_name=selected_bank_name,
                                branch_name=request.POST.get('branch_name', ''),
                                ifsc_code=request.POST.get('ifscCode', ''),
                                account_number=account_number
                            )
                        else:
                            for bank_instance in bank_queryset:
                                bank_instance.branch_name = request.POST.get('branch_name', '')
                                bank_instance.ifsc_code = request.POST.get('ifscCode', '')
                                bank_instance.save()

                            selected_bank = bank_queryset.first()

                       

                        if Fin_BankHolder.objects.filter(
                            Q(Account_number=selected_bank.account_number) |
                            Q(phone_number=phone_number) |
                            Q(Pan_it_number=pan_it_number) |
                            Q(Email=email),
                            Company=com if data.User_Type == "Company" else com.company_id
                        ).exclude(id=id).exists():
                            error_message_account = "Account details are already in use by another holder."
                            print(f"Error: {error_message_account}")
                            context = {
                                'bank': bank_queryset,
                                'error_message_account': error_message_account,
                                'com': com, 
                                'allmodules': allmodules,
                                'data': data,
                                'account_holder' : account_holder,
                            }
                            return render(request, 'company/Fin_Editbankholder.html', context)


                                                                                                                    
                    account_holder.banking_details = selected_bank
                    account_holder.Bank_name = selected_bank.bank_name
                    account_holder.Account_number = selected_bank.account_number
                    account_holder.Branch_name = selected_bank.branch_name
                    account_holder.Ifsc_code = selected_bank.ifsc_code

                    account_holder.save()

                    Fin_BankHolderHistory.objects.create(
                        LoginDetails=data,
                        Company=com if data.User_Type == "Company" else com.company_id,
                        Holder=account_holder,
                        date=date,
                        action='Edited'
                    )
                    return redirect('Fin_Bankholderview', id)

                except IntegrityError as e:
                    error_message_phone = ""
                    error_message_email = ""
                    error_message_account = ""

                    if 'phone_number' in str(e):
                        error_message_phone = "Phone number is already in use by another holder."
                    elif 'email' in str(e):
                        error_message_email = "Email is already in use by another holder."
                    elif 'account_number' in str(e):
                        error_message_account = "Account number is already in use by another holder."
                    else:
                        error_message_account = "Error in creating bank holder."
                    
                    bank_queryset = Fin_Banking.objects.all()
                    context = {
                        'bank': selected_bank,
                        'account_holder': account_holder, 
                        'error_message_phone': error_message_phone,
                        'error_message_email': error_message_email,
                        'error_message_account': error_message_account,
                        'account_holder': account_holder,
                    }
                    return render(request, 'company/Fin_Editbankholder.html', context)

            bank_queryset = Fin_Banking.objects.filter(company=com if data.User_Type == "Company" else com.company_id)
            context = {'bank': bank_queryset, 'account_holder': account_holder}
            return render(request, 'company/Fin_Editbankholder.html', context)

        except Fin_Login_Details.DoesNotExist:
            return redirect('/')

    return redirect('Fin_bankholder')


def Fin_deleteholder(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        try:
            data = Fin_Login_Details.objects.get(id=s_id)
            if data.User_Type == "Company":
                com = Fin_Company_Details.objects.get(Login_Id=s_id)
            else:
                staff_details = Fin_Staff_Details.objects.get(Login_Id=s_id)
                com = staff_details.company_id 
            try:
                account_holder = Fin_BankHolder.objects.get(id=id, Company=com)
                banking_details = account_holder.banking_details
                Fin_BankHolderComment.objects.filter(Holder_id=account_holder).delete()
                Fin_BankHolderHistory.objects.filter(Holder_id=account_holder).delete()
                account_holder.delete()
                banking_details.delete()
                return redirect('Fin_bankholder')
            except Fin_BankHolder.DoesNotExist:
                message = f"Fin_BankHolder instance with ID {id} does not exist for the company {com}"
                return render(request, '404.html', {'message': message}, status=404)
        except Fin_Login_Details.DoesNotExist:
            return redirect('/')  
    return redirect('Fin_bankholder')

def Fin_addcomment(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        try:
            data = Fin_Login_Details.objects.get(id=s_id)

            if data.User_Type == "Company":
                com = Fin_Company_Details.objects.get(Login_Id=s_id)
            else:
                staff_details = Fin_Staff_Details.objects.get(Login_Id=s_id)
                com = staff_details.company_id

            account_holder = get_object_or_404(Fin_BankHolder, id=id)

            if request.method == 'POST':
                comment_text = request.POST.get('comment')
                print("Received Comment Text:", comment_text)

                comment = Fin_BankHolderComment.objects.create(
                    comment_text=comment_text,
                    Holder=account_holder,
                    LoginDetails=data,
                    Company=com
                )
                comment.save()
                print("Comment Saved in the Database")

            comments = Fin_BankHolderComment.objects.filter(Holder=account_holder, Company=com)
            print("Comments in view:", comments)

            if account_holder.id is not None:
                return redirect(reverse('Fin_Bankholderview', kwargs={'id': id}))
            else:
                return HttpResponse("Invalid account holder ID")

        except Fin_Login_Details.DoesNotExist:
            print("Error: Fin_Login_Details.DoesNotExist")
            return redirect('/')

    print("Redirecting to /")
    return redirect('/') 



def Fin_deletecomment(request, id):
    comment = get_object_or_404(Fin_BankHolderComment, id=id)
    comment.delete() 
    return redirect(reverse('Fin_addcomment', args=[comment.Holder.id]))



def Fin_Bankhistory(request, holder_id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        try:
            data = Fin_Login_Details.objects.get(id=s_id)

            if data.User_Type == "Company":
                com = Fin_Company_Details.objects.get(Login_Id=s_id)
                allmodules = Fin_Modules_List.objects.get(Login_Id=s_id,status='New')
                account_holder = get_object_or_404(Fin_BankHolder, id=holder_id, Company=com)
                history = Fin_BankHolderHistory.objects.filter(Holder=account_holder).order_by('-date')
            else:
                com = Fin_Staff_Details.objects.get(Login_Id=s_id)
                # com = staff_details.company_id
                allmodules = Fin_Modules_List.objects.get(company_id=com.company_id, status='New')
                account_holder = get_object_or_404(Fin_BankHolder, id=holder_id, Company=com.company_id)
                history = Fin_BankHolderHistory.objects.filter(Holder=account_holder).order_by('-date')


            context = {
                'account_holder': account_holder,
                'history': history,
                'allmodules':allmodules,
                'com':com,
                'data':data,
            }
            return render(request, 'company/Fin_BankHistory.html', context)
        except Fin_Login_Details.DoesNotExist:
            return redirect('/')  
    return redirect('/')
        
# -------------Shemeem--------Price List & Customers-------------------------------

# PriceList

def Fin_priceList(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            list = Fin_Price_List.objects.filter(Company = com)
            return render(request,'company/Fin_Price_List.html',{'allmodules':allmodules,'com':com,'data':data,'list':list})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            list = Fin_Price_List.objects.filter(Company = com.company_id)
            return render(request,'company/Fin_Price_List.html',{'allmodules':allmodules,'com':com,'data':data,'list':list})
    else:
       return redirect('/')
    
def Fin_addPriceList(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            items = Fin_Items.objects.filter(Company = com, status = 'Active').order_by('name')
            return render(request,'company/Fin_Add_Price_List.html',{'allmodules':allmodules,'com':com,'data':data,'items':items})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            items = Fin_Items.objects.filter(Company = com.company_id, status = 'Active').order_by('name')
            return render(request,'company/Fin_Add_Price_List.html',{'allmodules':allmodules,'com':com,'data':data,'items':items})
    else:
       return redirect('/')

def Fin_createPriceList(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        if request.method == 'POST':
            name = request.POST['name']
            type = request.POST['type']
            itemRate = request.POST['item_rate']
            description = request.POST['description']
            upOrDown = request.POST['up_or_down']
            percent = request.POST['percentage']
            roundOff = request.POST['round_off']
            currency = request.POST['currency']

            if Fin_Price_List.objects.filter(Company = com, name__iexact = name).exists():
                res = f'<script>alert("{name} already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)

            priceList = Fin_Price_List(
                Company = com, LoginDetails = data, name = name, type = type, item_rate = itemRate, description = description, currency = currency, up_or_down = upOrDown, percentage = percent, round_off = roundOff, status = 'Active'
            )
            priceList.save()

            #save transaction

            Fin_PriceList_Transaction_History.objects.create(
                Company = com,
                LoginDetails = data,
                list = priceList,
                action = 'Created'
            )

            if itemRate == 'Customized individual rate':
                itemName = request.POST.getlist('itemName[]')
                stdRate = request.POST.getlist('itemRateSale[]') if type == 'Sales' else request.POST.getlist('itemRatePurchase[]')
                customRate = request.POST.getlist('customRate[]')
                
                if len(itemName) == len(stdRate) == len(customRate):
                    values = zip(itemName,stdRate,customRate)
                    lis = list(values)

                    for ele in lis:
                        Fin_PriceList_Items.objects.get_or_create(Company = com, LoginDetails = data, list = priceList, item = Fin_Items.objects.get(id = int(ele[0])), standard_rate = float(ele[1]), custom_rate = float(ele[2]))

                    return redirect(Fin_priceList)

                return redirect(Fin_addPriceList)

            return redirect(Fin_priceList)

        else:
                return redirect(Fin_addPriceList)
    else:
        return redirect('/')

def Fin_viewPriceList(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        list = Fin_Price_List.objects.get(id = id)
        plItems = Fin_PriceList_Items.objects.filter(list = list)
        cmt = Fin_PriceList_Comments.objects.filter(list = list)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            hist = Fin_PriceList_Transaction_History.objects.filter(Company = com, list = list).last()
            return render(request,'company/Fin_View_PriceList.html',{'allmodules':allmodules,'com':com,'data':data,'plItems':plItems, 'list':list, 'comments':cmt, 'history': hist})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            hist = Fin_PriceList_Transaction_History.objects.filter(Company = com.company_id, list = list).last()
            return render(request,'company/Fin_View_PriceList.html',{'allmodules':allmodules,'com':com,'data':data,'plItems':plItems, 'list':list, 'comments':cmt, 'history': hist})
    else:
       return redirect('/')
    
def Fin_changePriceListStatus(request,id,status):
    if 's_id' in request.session:
        list = Fin_Price_List.objects.get(id = id)
        list.status = status
        list.save()
        return redirect(Fin_viewPriceList, id)
    
def Fin_deletePriceList(request, id):
    if 's_id' in request.session:
        list = Fin_Price_List.objects.get( id = id)
        list.delete()
        return redirect(Fin_priceList)
    
def Fin_addPriceListComment(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        list = Fin_Price_List.objects.get(id = id)
        if request.method == "POST":
            cmt = request.POST['comment'].strip()

            Fin_PriceList_Comments.objects.create(Company = com, list = list, comments = cmt)
            return redirect(Fin_viewPriceList, id)
        return redirect(Fin_viewPriceList, id)
    return redirect('/')

def Fin_deletePriceListComment(request,id):
    if 's_id' in request.session:
        cmt = Fin_PriceList_Comments.objects.get(id = id)
        listId = cmt.list.id
        cmt.delete()
        return redirect(Fin_viewPriceList, listId)

def Fin_priceListHistory(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        list = Fin_Price_List.objects.get(id = id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            his = Fin_PriceList_Transaction_History.objects.filter(Company = com , list = list)
            return render(request,'company/Fin_PriceList_History.html',{'allmodules':allmodules,'com':com,'data':data,'history':his, 'list':list})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            his = Fin_PriceList_Transaction_History.objects.filter(Company = com.company_id , list = list)
            return render(request,'company/Fin_PriceList_History.html',{'allmodules':allmodules,'com':com,'data':data,'history':his, 'list':list})
    else:
       return redirect('/')
    
def Fin_editPriceList(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        list = Fin_Price_List.objects.get(id = id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            plItems = Fin_PriceList_Items.objects.filter(Company = com, list = list)
            items = Fin_Items.objects.filter(Company = com, status = 'Active').order_by('name')
            return render(request,'company/Fin_Edit_Price_List.html',{'allmodules':allmodules,'com':com,'data':data,'list':list, 'plItems':plItems, 'items':items })
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            plItems = Fin_PriceList_Items.objects.filter(Company = com.company_id, list = list)
            items = Fin_Items.objects.filter(Company = com.company_id, status = 'Active').order_by('name')
            return render(request,'company/Fin_Edit_Price_List.html',{'allmodules':allmodules,'com':com,'data':data,'list':list, 'plItems':plItems, 'items':items })
    else:
       return redirect('/')

def Fin_updatePriceList(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        lst = Fin_Price_List.objects.get(id = id)
        if request.method == 'POST':
            name = request.POST['name']
            type = request.POST['type']
            itemRate = request.POST['item_rate']
            description = request.POST['description']
            upOrDown = request.POST['up_or_down']
            percent = request.POST['percentage']
            roundOff = request.POST['round_off']
            currency = request.POST['currency']

            if lst.name != name and Fin_Price_List.objects.filter(Company = com, name__iexact = name).exists():
                res = f'<script>alert("{name} already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)

            if lst.item_rate == 'Customized individual rate' and itemRate != 'Customized individual rate':
                Fin_PriceList_Items.objects.filter(list = lst).delete()

            lst.name = name
            lst.type = type
            lst.item_rate = itemRate
            lst.description = description
            lst.currency = currency
            lst.up_or_down = upOrDown
            if itemRate == 'Customized individual rate':
                lst.percentage = None
                lst.round_off = None
            else:
                lst.percentage = percent
                lst.round_off = roundOff
            lst.save()

            #save transaction

            Fin_PriceList_Transaction_History.objects.create(
                Company = com,
                LoginDetails = data,
                list = lst,
                action = 'Edited'
            )

            itemName = request.POST.getlist('itemName[]')
            stdRate = request.POST.getlist('itemRateSale[]') if type == 'Sales' else request.POST.getlist('itemRatePurchase[]')
            customRate = request.POST.getlist('customRate[]')
            
            if itemRate == 'Customized individual rate':
                if Fin_PriceList_Items.objects.filter(list = lst).exists():
                    ids = request.POST.getlist('plItemId[]')
                    
                    if len(ids) == len(itemName) == len(stdRate) == len(customRate):
                        values = zip(ids, itemName,stdRate,customRate)
                        lis = list(values)

                        for ele in lis:
                            Fin_PriceList_Items.objects.filter(id = ele[0]).update(Company = com, LoginDetails = data, list = lst, item = Fin_Items.objects.get(id = int(ele[1])), standard_rate = float(ele[2]), custom_rate = float(ele[3]))

                        return redirect(Fin_viewPriceList,id)

                    else:
                        return redirect(Fin_editPriceList, id)
                else:
                    if len(itemName) == len(stdRate) == len(customRate):
                        values = zip(itemName,stdRate,customRate)
                        lis = list(values)
                        for ele in lis:
                            Fin_PriceList_Items.objects.create(Company = com, LoginDetails = data, list = lst, item = Fin_Items.objects.get(id = int(ele[0])), standard_rate = float(ele[1]), custom_rate = float(ele[2]))
                        
                        return redirect(Fin_viewPriceList,id)
            else:
                return redirect(Fin_viewPriceList,id)

        else:
            return redirect(Fin_editPriceList, id)
    else:
        return redirect('/')

def Fin_priceListViewPdf(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        lst = Fin_Price_List.objects.get(id = id)
        plItems = Fin_PriceList_Items.objects.filter(list = lst)
    
        context = {'list': lst, 'plItems':plItems}
        
        template_path = 'company/Fin_PriceListView_Pdf.html'
        fname = 'Price_List_'+lst.name
        # return render(request, 'company/Fin_PriceListView_Pdf.html',context)
        # Create a Django response object, and specify content_type as pdftemp_
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] =f'attachment; filename = {fname}.pdf'
        # find the template and render it.
        template = get_template(template_path)
        html = template.render(context)

        # create a pdf
        pisa_status = pisa.CreatePDF(
        html, dest=response)
        # if error then show some funny view
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
    else:
        return redirect('/')

def Fin_sharePriceListViewToEmail(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        lst = Fin_Price_List.objects.get(id = id)
        plItems = Fin_PriceList_Items.objects.filter(list = lst)
        try:
            if request.method == 'POST':
                emails_string = request.POST['email_ids']

                # Split the string by commas and remove any leading or trailing whitespace
                emails_list = [email.strip() for email in emails_string.split(',')]
                email_message = request.POST['email_message']
                # print(emails_list)
            
                context = {'list': lst, 'plItems':plItems}
                template_path = 'company/Fin_PriceListView_Pdf.html'
                template = get_template(template_path)

                html  = template.render(context)
                result = BytesIO()
                pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
                pdf = result.getvalue()
                filename = f'Price_list_{lst.name}.pdf'
                subject = f"Price_list_{lst.name}"
                email = EmailMessage(subject, f"Hi,\nPlease find the attached Price List details - Price List-{lst.name}. \n{email_message}\n\n--\nRegards,\n{com.Company_name}\n{com.Address}\n{com.State} - {com.Country}\n{com.Contact}", from_email=settings.EMAIL_HOST_USER, to=emails_list)
                email.attach(filename, pdf, "application/pdf")
                email.send(fail_silently=False)

                messages.success(request, 'Price List details has been shared via email successfully..!')
                return redirect(Fin_viewPriceList,id)
        except Exception as e:
            print(e)
            messages.error(request, f'{e}')
            return redirect(Fin_viewPriceList, id)


# Customers
        
def Fin_customers(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            cust = Fin_Customers.objects.filter(Company = com)
            return render(request,'company/Fin_Customers.html',{'allmodules':allmodules,'com':com,'data':data,'customers':cust})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            cust = Fin_Customers.objects.filter(Company = com.company_id)
            return render(request,'company/Fin_Customers.html',{'allmodules':allmodules,'com':com,'data':data,'customers':cust})
    else:
       return redirect('/')

def Fin_addCustomer(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            trms = Fin_Company_Payment_Terms.objects.filter(Company = com)
            lst = Fin_Price_List.objects.filter(Company = com, status = 'Active')
            return render(request,'company/Fin_Add_Customer.html',{'allmodules':allmodules,'com':com,'data':data, 'pTerms':trms, 'list':lst})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            trms = Fin_Company_Payment_Terms.objects.filter(Company = com.company_id)
            lst = Fin_Price_List.objects.filter(Company = com.company_id, status = 'Active')
            return render(request,'company/Fin_Add_Customer.html',{'allmodules':allmodules,'com':com,'data':data, 'pTerms':trms, 'list':lst})
    else:
       return redirect('/')

def Fin_checkCustomerName(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        fName = request.POST['fname']
        lName = request.POST['lname']

        if Fin_Customers.objects.filter(Company = com, first_name__iexact = fName, last_name__iexact = lName).exists():
            msg = f'{fName} {lName} already exists, Try another.!'
            return JsonResponse({'is_exist':True, 'message':msg})
        else:
            return JsonResponse({'is_exist':False})
    else:
        return redirect('/')
    
def Fin_checkCustomerGSTIN(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        gstIn = request.POST['gstin']

        if Fin_Customers.objects.filter(Company = com, gstin__iexact = gstIn).exists():
            msg = f'{gstIn} already exists, Try another.!'
            return JsonResponse({'is_exist':True, 'message':msg})
        else:
            return JsonResponse({'is_exist':False})
    else:
        return redirect('/')
    
def Fin_checkCustomerPAN(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        pan = request.POST['pan']

        if Fin_Customers.objects.filter(Company = com, pan_no__iexact = pan).exists():
            msg = f'{pan} already exists, Try another.!'
            return JsonResponse({'is_exist':True, 'message':msg})
        else:
            return JsonResponse({'is_exist':False})
    else:
        return redirect('/')

def Fin_checkCustomerPhone(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        phn = request.POST['phone']

        if Fin_Customers.objects.filter(Company = com, mobile__iexact = phn).exists():
            msg = f'{phn} already exists, Try another.!'
            return JsonResponse({'is_exist':True, 'message':msg})
        else:
            return JsonResponse({'is_exist':False})
    else:
        return redirect('/')

def Fin_checkCustomerEmail(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        email = request.POST['email']

        if Fin_Customers.objects.filter(Company = com, email__iexact = email).exists():
            msg = f'{email} already exists, Try another.!'
            return JsonResponse({'is_exist':True, 'message':msg})
        else:
            return JsonResponse({'is_exist':False})
    else:
        return redirect('/')
    
def Fin_createCustomer(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        if request.method == 'POST':
            fName = request.POST['first_name']
            lName = request.POST['last_name']
            gstIn = request.POST['gstin']
            pan = request.POST['pan_no']
            email = request.POST['email']
            phn = request.POST['mobile']

            if Fin_Customers.objects.filter(Company = com, first_name__iexact = fName, last_name__iexact = lName).exists():
                res = f'<script>alert("Customer `{fName} {lName}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)
            elif Fin_Customers.objects.filter(Company = com, gstin__iexact = gstIn).exists():
                res = f'<script>alert("GSTIN `{gstIn}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)
            elif Fin_Customers.objects.filter(Company = com, pan_no__iexact = pan).exists():
                res = f'<script>alert("PAN No `{pan}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)
            elif Fin_Customers.objects.filter(Company = com, mobile__iexact = phn).exists():
                res = f'<script>alert("Phone Number `{phn}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)
            elif Fin_Customers.objects.filter(Company = com, email__iexact = email).exists():
                res = f'<script>alert("Email `{email}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)

            cust = Fin_Customers(
                Company = com,
                LoginDetails = data,
                title = request.POST['title'],
                first_name = fName,
                last_name = lName,
                company = request.POST['company_name'],
                location = request.POST['location'],
                place_of_supply = request.POST['place_of_supply'],
                gst_type = request.POST['gst_type'],
                gstin = None if request.POST['gst_type'] == "Unregistered Business" or request.POST['gst_type'] == 'Overseas' or request.POST['gst_type'] == 'Consumer' else gstIn,
                pan_no = pan,
                email = email,
                mobile = phn,
                website = request.POST['website'],
                price_list = None if request.POST['price_list'] ==  "" else Fin_Price_List.objects.get(id = request.POST['price_list']),
                payment_terms = None if request.POST['payment_terms'] == "" else Fin_Company_Payment_Terms.objects.get(id = request.POST['payment_terms']),
                opening_balance = 0 if request.POST['open_balance'] == "" else float(request.POST['open_balance']),
                open_balance_type = request.POST['balance_type'],
                current_balance = 0 if request.POST['open_balance'] == "" else float(request.POST['open_balance']),
                credit_limit = 0 if request.POST['credit_limit'] == "" else float(request.POST['credit_limit']),
                billing_street = request.POST['street'],
                billing_city = request.POST['city'],
                billing_state = request.POST['state'],
                billing_pincode = request.POST['pincode'],
                billing_country = request.POST['country'],
                ship_street = request.POST['shipstreet'],
                ship_city = request.POST['shipcity'],
                ship_state = request.POST['shipstate'],
                ship_pincode = request.POST['shippincode'],
                ship_country = request.POST['shipcountry'],
                status = 'Active'
            )
            cust.save()

            #save transaction

            Fin_Customers_History.objects.create(
                Company = com,
                LoginDetails = data,
                customer = cust,
                action = 'Created'
            )

            return redirect(Fin_customers)

        else:
            return redirect(Fin_addCustomer)
    else:
        return redirect('/')

def Fin_newCustomerPaymentTerm(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        term = request.POST['term']
        days = request.POST['days']

        if not Fin_Company_Payment_Terms.objects.filter(Company = com, term_name__iexact = term).exists():
            Fin_Company_Payment_Terms.objects.create(Company = com, term_name = term, days =days)
            
            list= []
            terms = Fin_Company_Payment_Terms.objects.filter(Company = com)

            for term in terms:
                termDict = {
                    'name': term.term_name,
                    'id': term.id
                }
                list.append(termDict)

            return JsonResponse({'status':True,'terms':list},safe=False)
        else:
            return JsonResponse({'status':False})

    else:
        return redirect('/')

def Fin_viewCustomer(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        cust = Fin_Customers.objects.get(id = id)
        cmt = Fin_Customers_Comments.objects.filter(customer = cust)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            hist = Fin_Customers_History.objects.filter(Company = com, customer = cust).last()
            return render(request,'company/Fin_View_Customer.html',{'allmodules':allmodules,'com':com,'data':data, 'customer':cust, 'history':hist, 'comments':cmt})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            hist = Fin_Customers_History.objects.filter(Company = com.company_id, customer = cust).last()
            return render(request,'company/Fin_View_Customer.html',{'allmodules':allmodules,'com':com,'data':data, 'customer':cust, 'history':hist, 'comments':cmt})
    else:
       return redirect('/')

def Fin_changeCustomerStatus(request,id,status):
    if 's_id' in request.session:
        
        cust = Fin_Customers.objects.get(id = id)
        cust.status = status
        cust.save()
        return redirect(Fin_viewCustomer, id)
    
def Fin_deleteCustomer(request, id):
    if 's_id' in request.session:
        cust = Fin_Customers.objects.get( id = id)
        cust.delete()
        return redirect(Fin_customers)
    
def Fin_customerHistory(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        cust = Fin_Customers.objects.get(id = id)
        his = Fin_Customers_History.objects.filter(customer = cust)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            return render(request,'company/Fin_Customer_History.html',{'allmodules':allmodules,'com':com,'data':data,'history':his, 'customer':cust})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            return render(request,'company/Fin_Customer_History.html',{'allmodules':allmodules,'com':com,'data':data,'history':his, 'customer':cust})
    else:
       return redirect('/')

def Fin_editCustomer(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        cust = Fin_Customers.objects.get(id = id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            trms = Fin_Company_Payment_Terms.objects.filter(Company = com)
            lst = Fin_Price_List.objects.filter(Company = com, status = 'Active')
            return render(request,'company/Fin_Edit_Customer.html',{'allmodules':allmodules,'com':com,'data':data, 'customer':cust, 'pTerms':trms, 'list':lst})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            trms = Fin_Company_Payment_Terms.objects.filter(Company = com.company_id)
            lst = Fin_Price_List.objects.filter(Company = com.company_id, status = 'Active')
            return render(request,'company/Fin_Edit_Customer.html',{'allmodules':allmodules,'com':com,'data':data, 'customer':cust, 'pTerms':trms, 'list':lst})
    else:
       return redirect('/')

def Fin_updateCustomer(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        cust = Fin_Customers.objects.get(id = id)

        if request.method == 'POST':
            fName = request.POST['first_name']
            lName = request.POST['last_name']
            gstIn = request.POST['gstin']
            pan = request.POST['pan_no']
            email = request.POST['email']
            phn = request.POST['mobile']

            if cust.first_name != fName and cust.last_name != lName and Fin_Customers.objects.filter(Company = com, first_name__iexact = fName, last_name__iexact = lName).exists():
                res = f'<script>alert("Customer `{fName} {lName}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)
            elif cust.gstin != gstIn and Fin_Customers.objects.filter(Company = com, gstin__iexact = gstIn).exists():
                res = f'<script>alert("GSTIN `{gstIn}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)
            elif cust.pan_no != pan and Fin_Customers.objects.filter(Company = com, pan_no__iexact = pan).exists():
                res = f'<script>alert("PAN No `{pan}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)
            elif cust.mobile != phn and Fin_Customers.objects.filter(Company = com, mobile__iexact = phn).exists():
                res = f'<script>alert("Phone Number `{phn}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)
            elif cust.email != email and Fin_Customers.objects.filter(Company = com, email__iexact = email).exists():
                res = f'<script>alert("Email `{email}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)

            # Updating customer details

            cust.title = request.POST['title']
            cust.first_name = fName
            cust.last_name = lName
            cust.company = request.POST['company_name']
            cust.location = request.POST['location']
            cust.place_of_supply = request.POST['place_of_supply']
            cust.gst_type = request.POST['gst_type']
            cust.gstin = None if request.POST['gst_type'] == "Unregistered Business" or request.POST['gst_type'] == 'Overseas' or request.POST['gst_type'] == 'Consumer' else gstIn
            cust.pan_no = pan
            cust.email = email
            cust.mobile = phn
            cust.website = request.POST['website']
            cust.price_list = None if request.POST['price_list'] ==  "" else Fin_Price_List.objects.get(id = request.POST['price_list'])
            cust.payment_terms = None if request.POST['payment_terms'] == "" else Fin_Company_Payment_Terms.objects.get(id = request.POST['payment_terms'])
            cust.opening_balance = 0 if request.POST['open_balance'] == "" else float(request.POST['open_balance'])
            cust.open_balance_type = request.POST['balance_type']
            cust.current_balance = 0 if request.POST['open_balance'] == "" else float(request.POST['open_balance'])
            cust.credit_limit = 0 if request.POST['credit_limit'] == "" else float(request.POST['credit_limit'])
            cust.billing_street = request.POST['street']
            cust.billing_city = request.POST['city']
            cust.billing_state = request.POST['state']
            cust.billing_pincode = request.POST['pincode']
            cust.billing_country = request.POST['country']
            cust.ship_street = request.POST['shipstreet']
            cust.ship_city = request.POST['shipcity']
            cust.ship_state = request.POST['shipstate']
            cust.ship_pincode = request.POST['shippincode']
            cust.ship_country = request.POST['shipcountry']

            cust.save()

            #save transaction

            Fin_Customers_History.objects.create(
                Company = com,
                LoginDetails = data,
                customer = cust,
                action = 'Edited'
            )

            return redirect(Fin_viewCustomer, id)

        else:
            return redirect(Fin_editCustomer, id)
    else:
        return redirect('/')

def Fin_customerTransactionsPdf(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        cust = Fin_Customers.objects.get(id = id)
    
        context = {'customer':cust}
        
        template_path = 'company/Fin_Customer_Transaction_Pdf.html'
        fname = 'Customer_Transactions_'+cust.first_name+'_'+cust.last_name
        # return render(request, 'company/Fin_Customer_Transaction_Pdf.html',context)
        # Create a Django response object, and specify content_type as pdftemp_
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] =f'attachment; filename = {fname}.pdf'
        # find the template and render it.
        template = get_template(template_path)
        html = template.render(context)

        # create a pdf
        pisa_status = pisa.CreatePDF(
        html, dest=response)
        # if error then show some funny view
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
    else:
        return redirect('/')

def Fin_shareCustomerTransactionsToEmail(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        cust = Fin_Customers.objects.get(id = id)
        try:
            if request.method == 'POST':
                emails_string = request.POST['email_ids']

                # Split the string by commas and remove any leading or trailing whitespace
                emails_list = [email.strip() for email in emails_string.split(',')]
                email_message = request.POST['email_message']
                # print(emails_list)
            
                context = {'customer': cust}
                template_path = 'company/Fin_Customer_Transaction_Pdf.html'
                template = get_template(template_path)

                html  = template.render(context)
                result = BytesIO()
                pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
                pdf = result.getvalue()
                filename = f'Customer_Transactions_{cust.first_name}_{cust.last_name}'
                subject = f"Customer_Transactions_{cust.first_name}_{cust.last_name}"
                email = EmailMessage(subject, f"Hi,\nPlease find the attached Transaction details for - Customer-{cust.first_name} {cust.last_name}. \n{email_message}\n\n--\nRegards,\n{com.Company_name}\n{com.Address}\n{com.State} - {com.Country}\n{com.Contact}", from_email=settings.EMAIL_HOST_USER, to=emails_list)
                email.attach(filename, pdf, "application/pdf")
                email.send(fail_silently=False)

                messages.success(request, 'Transactions details has been shared via email successfully..!')
                return redirect(Fin_viewCustomer,id)
        except Exception as e:
            print(e)
            messages.error(request, f'{e}')
            return redirect(Fin_viewCustomer, id)

def Fin_addCustomerComment(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        cust = Fin_Customers.objects.get(id = id)
        if request.method == "POST":
            cmt = request.POST['comment'].strip()

            Fin_Customers_Comments.objects.create(Company = com, customer = cust, comments = cmt)
            return redirect(Fin_viewCustomer, id)
        return redirect(Fin_viewCustomer, id)
    return redirect('/')

def Fin_deleteCustomerComment(request,id):
    if 's_id' in request.session:
        cmt = Fin_Customers_Comments.objects.get(id = id)
        custId = cmt.customer.id
        cmt.delete()
        return redirect(Fin_viewCustomer, custId)
        
# End

# harikrishnan start------------------------------
    
def employee_list(request):
    sid = request.session['s_id']
    loginn = Fin_Login_Details.objects.get(id=sid)
    if loginn.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        employee = Employee.objects.filter(company_id=com.id)
    elif loginn.User_Type == 'Staff' :
        com = Fin_Staff_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
        employee = Employee.objects.filter(company_id=com.company_id_id)
    else:
        distributor = Fin_Distributors_Details.objects.get(Login_Id = sid)

    return render(request,'company/Employee_List.html',{'employee':employee,'allmodules':allmodules,'com':com,'data':loginn})

def employee_create_page(request):
    sid = request.session['s_id']
    loginn = Fin_Login_Details.objects.get(id=sid)
    
    if loginn.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        bloodgroup = Employee_Blood_Group.objects.filter(company_id=com.id,login_id=sid).values('blood_group').distinct()
        
    elif loginn.User_Type == 'Staff' :
        staf = Fin_Staff_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = staf.company_id_id)
        bloodgroup = Employee_Blood_Group.objects.filter(company_id=staf.company_id_id,login_id=sid).values('blood_group').distinct()

    return render(request,'company/Employee_Create_Page.html',{'allmodules':allmodules,'bloodgroup':bloodgroup})    

def employee_save(request):

    if request.method == 'POST':

        title = request.POST['Title']
        firstname = request.POST['First_Name'].capitalize()
        lastname = request.POST['Last_Name'].capitalize()
        alias = request.POST['Alias']
        joiningdate = request.POST['Joining_Date']
        salarydate = request.POST['Salary_Date']
        salaryamount = request.POST['Salary_Amount']

        if request.POST['Salary_Amount'] == '':
            salaryamount = None
        else:
            salaryamount = request.POST['Salary_Amount']

        amountperhour = request.POST['perhour']
        if amountperhour == '' or amountperhour == '0':
            amountperhour = 0
        else:
            amountperhour = request.POST['perhour']

        workinghour = request.POST['workhour']
        if workinghour == '' or workinghour == '0':
            workinghour = 0
        else:
            workinghour = request.POST['workhour']

        salary_type = request.POST['Salary_Type']
        
        employeenumber = request.POST['Employee_Number']
        designation = request.POST['Designation']
        location = request.POST['Location']
        gender = request.POST['Gender']
        image = request.FILES.get('Image', None)
        if image:
            image = request.FILES['Image']
        else:
            image = ''

        dob = request.POST['DOB']
        blood = request.POST['Blood']
        parent = request.POST['Parent'].capitalize()
        spouse = request.POST['Spouse'].capitalize()
        street = request.POST['street']
        city = request.POST['city']
        state = request.POST['state']
        pincode = request.POST['pincode']
        country = request.POST['country']
        tempStreet = request.POST['tempStreet']
        tempCity = request.POST['tempCity']
        tempState = request.POST['tempState']
        tempPincode = request.POST['tempPincode']
        tempCountry = request.POST['tempCountry']
        
        
        contact = request.POST['Contact_Number']
        emergencycontact = request.POST['Emergency_Contact']
        email = request.POST['Email']
        file = request.FILES.get('File', None)
        if file:
            file = request.FILES['File']
        else:
            file=''
        bankdetails = request.POST['Bank_Details']
        accoutnumber = request.POST['Account_Number']
        ifsc = request.POST['IFSC']
        bankname = request.POST['BankName']
        branchname = request.POST['BranchName']
        transactiontype = request.POST['Transaction_Type']

        

        if request.POST['tds_applicable'] == 'Yes':
            tdsapplicable = request.POST['tds_applicable']
            tdstype = request.POST['TDS_Type']
            
            if tdstype == 'Amount':
                tdsvalue = request.POST['TDS_Amount']
            elif tdstype == 'Percentage':
                tdsvalue = request.POST['TDS_Percentage']
            else:
                tdsvalue = 0
        elif request.POST['tds_applicable'] == 'No':
            tdsvalue = 0
            tdstype = ''
            tdsapplicable = request.POST['tds_applicable']
        else:
            tdsvalue = 0
            tdstype = ''
            tdsapplicable = ''

        
        
        incometax = request.POST['Income_Tax']
        aadhar = request.POST['Aadhar']
        uan = request.POST['UAN']
        pf = request.POST['PF']
        pan = request.POST['PAN']
        pr = request.POST['PR']

        if dob == '':
            age = 2
        else:
            dob2 = date.fromisoformat(dob)
            today = date.today()
            age = int(today.year - dob2.year - ((today.month, today.day) < (dob2.month, dob2.day)))
        
        sid = request.session['s_id']
        employee = Fin_Login_Details.objects.get(id=sid)
        
        if employee.User_Type == 'Company':
            companykey =  Fin_Company_Details.objects.get(Login_Id_id=sid)
        elif employee.User_Type == 'Staff':
            staffkey = Fin_Staff_Details.objects.get(Login_Id=sid)
            companykey = Fin_Company_Details.objects.get(id=staffkey.company_id_id)
        else:
            distributorkey = Fin_Distributors_Details.objects.get(login_Id=sid)
            companykey = Fin_Company_Details.objects.get(id=distributorkey.company_id_id)

        
        if Employee.objects.filter(employee_mail=email,mobile = contact,employee_number=employeenumber,company_id = companykey.id).exists():
            messages.error(request,'user exist')
            return redirect('employee_create_page')
        
        elif Employee.objects.filter(mobile = contact,company_id = companykey.id).exists():
            messages.error(request,'phone number exist')
            return redirect('employee_create_page')
        
        elif Employee.objects.filter(emergency_contact = emergencycontact,company_id = companykey.id).exists():
            messages.error(request,'emergency phone number exist')
            return redirect('employee_create_page')
        
        elif Employee.objects.filter(employee_mail=email,company_id = companykey.id).exists():
            messages.error(request,'email exist')
            return redirect('employee_create_page')
        
        elif Employee.objects.filter(employee_number=employeenumber,company_id = companykey.id).exists():
            messages.error(request,'employee id exist')
            return redirect('employee_create_page')
        
        elif incometax != '' and Employee.objects.filter(income_tax_number = incometax,company_id = companykey.id).exists():
            messages.error(request,'Income Tax Number exist')
            return redirect('employee_create_page')
        
        elif pf != '' and Employee.objects.filter(pf_account_number = pf,company_id = companykey.id).exists():
            messages.error(request,'PF account number exist')
            return redirect('employee_create_page')
        
        elif aadhar != '' and Employee.objects.filter(aadhar_number = aadhar,company_id = companykey.id).exists():
            messages.error(request,'Aadhar number exist')
            return redirect('employee_create_page')
        
        elif pan != '' and Employee.objects.filter(pan_number = pan,company_id = companykey.id).exists():
            messages.error(request,'PAN number exist')
            return redirect('employee_create_page')
        
        elif uan != '' and Employee.objects.filter(universal_account_number = uan,company_id = companykey.id).exists():
            messages.error(request,'Universal account number exist')
            return redirect('employee_create_page')
        
        elif pr != '' and Employee.objects.filter(pr_account_number = pr,company_id = companykey.id).exists():
            messages.error(request,'PR account number exist')
            return redirect('employee_create_page')
        
        elif bankdetails.lower() == 'yes':
            if accoutnumber != '' and Employee.objects.filter(account_number=accoutnumber,company_id = companykey.id).exists():
                messages.error(request,'Bank account number already exist')
                return redirect('employee_create_page')
            
            else:
                if employee.User_Type == 'Company':
                    

                    new = Employee(upload_image=image,title = title,first_name = firstname,last_name = lastname,alias = alias,
                            employee_mail = email,employee_number = employeenumber,employee_designation = designation,
                            employee_current_location = location,mobile = contact,date_of_joining = joiningdate,
                            employee_status = 'Active' ,company_id = companykey.id,login_id=sid,salary_amount = salaryamount ,
                            amount_per_hour = amountperhour ,total_working_hours = workinghour,gender = gender ,date_of_birth = dob ,
                            age = age,blood_group = blood,fathers_name_mothers_name = parent,spouse_name = spouse,
                            emergency_contact = emergencycontact,provide_bank_details = bankdetails,account_number = accoutnumber,
                            ifsc = ifsc,name_of_bank = bankname,branch_name = branchname,bank_transaction_type = transactiontype,
                            tds_applicable = tdsapplicable, tds_type = tdstype,percentage_amount = tdsvalue,pan_number = pan,
                            income_tax_number = incometax,aadhar_number = aadhar,universal_account_number = uan,pf_account_number = pf,
                            pr_account_number = pr,upload_file = file,employee_salary_type =salary_type,salary_effective_from=salarydate,
                            city=city,street=street,state=state,country=country,pincode=pincode,temporary_city=tempCity,
                            temporary_street=tempStreet,temporary_state=tempState,temporary_pincode=tempPincode,temporary_country=tempCountry)
                    new.save()

                    history = Employee_History(company_id = companykey.id,login_id=sid,employee_id = new.id,date = date.today(),action = 'Created')
                    history.save()
            
                elif employee.User_Type == 'Staff':
                    

                    new =  Employee(upload_image=image,title = title,first_name = firstname,last_name = lastname,alias = alias,
                                employee_mail = email,employee_number = employeenumber,employee_designation = designation,
                                employee_current_location = location,mobile = contact,date_of_joining = joiningdate,
                                employee_salary_type = salary_type,employee_status = 'Active' ,company_id = companykey.id,login_id=sid ,
                                amount_per_hour = amountperhour ,total_working_hours = workinghour,gender = gender ,date_of_birth = dob ,
                                age = age,blood_group = blood,fathers_name_mothers_name = parent,spouse_name = spouse,
                                emergency_contact = emergencycontact,provide_bank_details = bankdetails,account_number = accoutnumber,
                                ifsc = ifsc,name_of_bank = bankname,branch_name = branchname,bank_transaction_type = transactiontype,
                                tds_applicable = tdsapplicable, tds_type = tdstype,percentage_amount = tdsvalue,pan_number = pan,
                                income_tax_number = incometax,aadhar_number = aadhar,universal_account_number = uan,pf_account_number = pf,
                                pr_account_number = pr,upload_file = file,salary_amount = salaryamount,salary_effective_from=salarydate,
                                city=city,street=street,state=state,country=country,pincode=pincode,temporary_city=tempCity,
                                temporary_street=tempStreet,temporary_state=tempState,temporary_pincode=tempPincode,temporary_country=tempCountry)
                    
                    new.save()

                    history = Employee_History(company_id = companykey.id,login_id=sid,employee_id = new.id,date = date.today(),action = 'Created')
                    history.save()
        
        else:
            if employee.User_Type == 'Company':
                

                new = Employee(upload_image=image,title = title,first_name = firstname,last_name = lastname,alias = alias,
                        employee_mail = email,employee_number = employeenumber,employee_designation = designation,
                        employee_current_location = location,mobile = contact,date_of_joining = joiningdate,
                        employee_status = 'Active' ,company_id = companykey.id,login_id=sid,salary_amount = salaryamount ,
                        amount_per_hour = amountperhour ,total_working_hours = workinghour,gender = gender ,date_of_birth = dob ,
                        age = age,blood_group = blood,fathers_name_mothers_name = parent,spouse_name = spouse,
                        emergency_contact = emergencycontact,provide_bank_details = bankdetails,account_number = accoutnumber,
                        ifsc = ifsc,name_of_bank = bankname,branch_name = branchname,bank_transaction_type = transactiontype,
                        tds_applicable = tdsapplicable, tds_type = tdstype,percentage_amount = tdsvalue,pan_number = pan,
                        income_tax_number = incometax,aadhar_number = aadhar,universal_account_number = uan,pf_account_number = pf,
                        pr_account_number = pr,upload_file = file,employee_salary_type =salary_type,salary_effective_from=salarydate,
                        city=city,street=street,state=state,country=country,pincode=pincode,temporary_city=tempCity,
                        temporary_street=tempStreet,temporary_state=tempState,temporary_pincode=tempPincode,temporary_country=tempCountry)
                new.save()

                history = Employee_History(company_id = companykey.id,login_id=sid,employee_id = new.id,date = date.today(),action = 'Created')
                history.save()
        
            elif employee.User_Type == 'Staff':
                

                new =  Employee(upload_image=image,title = title,first_name = firstname,last_name = lastname,alias = alias,
                            employee_mail = email,employee_number = employeenumber,employee_designation = designation,
                            employee_current_location = location,mobile = contact,date_of_joining = joiningdate,
                            employee_salary_type = salary_type,employee_status = 'Active' ,company_id = companykey.id,login_id=sid ,
                            amount_per_hour = amountperhour ,total_working_hours = workinghour,gender = gender ,date_of_birth = dob ,
                            age = age,blood_group = blood,fathers_name_mothers_name = parent,spouse_name = spouse,
                            emergency_contact = emergencycontact,provide_bank_details = bankdetails,account_number = accoutnumber,
                            ifsc = ifsc,name_of_bank = bankname,branch_name = branchname,bank_transaction_type = transactiontype,
                            tds_applicable = tdsapplicable, tds_type = tdstype,percentage_amount = tdsvalue,pan_number = pan,
                            income_tax_number = incometax,aadhar_number = aadhar,universal_account_number = uan,pf_account_number = pf,
                            pr_account_number = pr,upload_file = file,salary_amount = salaryamount,salary_effective_from=salarydate,
                            city=city,street=street,state=state,country=country,pincode=pincode,temporary_city=tempCity,
                            temporary_street=tempStreet,temporary_state=tempState,temporary_pincode=tempPincode,temporary_country=tempCountry)
                
                new.save()

                history = Employee_History(company_id = companykey.id,login_id=sid,employee_id = new.id,date = date.today(),action = 'Created')
                history.save()

        sid = request.session['s_id']
        loginn = Fin_Login_Details.objects.get(id=sid)
        if loginn.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = sid)
            allmodules = Fin_Modules_List.objects.get(company_id = com.id)
            employee = Employee.objects.filter(company_id=com.id)
            
        elif loginn.User_Type == 'Staff' :
            com = Fin_Staff_Details.objects.get(Login_Id = sid)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
            employee = Employee.objects.filter(company_id=com.company_id_id)
        return render(request,'company/Employee_List.html',{'allmodules':allmodules,'employee':employee,'com':com,'data':loginn})

def employee_overview(request,pk):
    employ = Employee.objects.get(id = pk)
    comments = Employee_Comment.objects.filter(employee_id = pk,company_id=employ.company_id)
    history = Employee_History.objects.filter(employee_id=pk,company_id=employ.company_id).latest('date')
    if comments.exists():
        for index, comment in enumerate(comments):
            comment.index = index + 1
    else: 
        index = '0'

    sid = request.session['s_id']
    loginn = Fin_Login_Details.objects.get(id=sid)
    if loginn.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        
    elif loginn.User_Type == 'Staff' :
        com = Fin_Staff_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
    return render(request,'company/Employee_Overview.html',{'index':index,'comments':comments ,'employ':employ,'allmodules':allmodules,'history':history,'com':com,'data':loginn})

def employee_delete(request,pk):
    employ = Employee.objects.get(id = pk)
    employ.delete()
    sid = request.session['s_id']
    loginn = Fin_Login_Details.objects.get(id=sid)
    if loginn.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        employee = Employee.objects.filter(company_id=com.id)
        
    elif loginn.User_Type == 'Staff' :
        com = Fin_Staff_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
        employee = Employee.objects.filter(company_id=com.company_id_id)
    return render(request,'company/Employee_List.html',{'employee':employee,'allmodules':allmodules,'com':com,'data':loginn})

def employee_comment(request,pk):
    employ = Employee.objects.get(id = pk)
    todayDate = date.today()
    sid = request.session['s_id']
    log_in = Fin_Login_Details.objects.get(id=sid)
    loginID = log_in.id
    

    if request.method == 'POST':
        comments = request.POST['comment']  
        employeeComment = Employee_Comment(employee_id=pk,company_id=employ.company_id,login_id=loginID,comment=comments,date=todayDate)
        employeeComment.save()
        comments = Employee_Comment.objects.filter(employee_id = pk,company_id=employ.company_id)
        history = Employee_History.objects.filter(employee_id=pk,company_id=employ.company_id).latest('date')
        if comments.exists():
            for index, comment in enumerate(comments):
                comment.index = index + 1
        else: 
            index = '0'

    
    
    if log_in.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        
    elif log_in.User_Type == 'Staff' :
        com = Fin_Staff_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
    return render(request,'company/Employee_Overview.html',{'employ':employ,'allmodules':allmodules,'index':index,'comments':comments ,'history':history})


def employee_comment_view(request,pk):
    employ = Employee.objects.get(id = pk)
    comments = Employee_Comment.objects.filter(employee_id = pk,company_id=employ.company_id)
    sid = request.session['s_id']
    loginn = Fin_Login_Details.objects.get(id=sid)
    if loginn.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        
    elif loginn.User_Type == 'Staff' :
        com = Fin_Staff_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
    return render(request,'company/Employee_Comment.html',{'comments':comments,'employ':employ,'allmodules':allmodules,'com':com,'data':loginn})

def employee_history(request,pk):
    employ = Employee.objects.get(id = pk)
    history = Employee_History.objects.filter(employee_id = pk,company_id=employ.company_id)
    sid = request.session['s_id']
    loginn = Fin_Login_Details.objects.get(id=sid)
    if loginn.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        
    elif loginn.User_Type == 'Staff' :
        com = Fin_Staff_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
    return render(request,'company/Employee_History.html',{'history':history,'employ':employ,'allmodules':allmodules,'com':com,'data':loginn})

def activate(request,pk):
    employ = Employee.objects.get(id = pk)
    if employ.employee_status == 'Active':
        employ.employee_status = 'Inactive'
    else:
        employ.employee_status = 'Active'
    employ.save()

    sid = request.session['s_id']
    loginn = Fin_Login_Details.objects.get(id=sid)
    if loginn.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        
    elif loginn.User_Type == 'Staff' :
        com = Fin_Staff_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)

    comments = Employee_Comment.objects.filter(employee_id = pk,company_id=employ.company_id)
    history = Employee_History.objects.filter(employee_id=pk,company_id=employ.company_id).latest('date')
    if comments.exists():
        for index, comment in enumerate(comments):
            comment.index = index + 1
    else: 
        index = '0'
    return render(request,'company/Employee_Overview.html',{'employ':employ,'allmodules':allmodules,'index':index,'comments':comments ,'history':history,'com':com,'data':loginn})

def employee_edit_page(request,pk):
    employe = Employee.objects.get(id=pk)
    sid = request.session['s_id']
    loginn = Fin_Login_Details.objects.get(id=sid)
    if loginn.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        bloodgroup = Employee_Blood_Group.objects.filter(company_id=com.id,login_id=sid).values('blood_group').distinct()
        
    elif loginn.User_Type == 'Staff' :
        com = Fin_Staff_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
        bloodgroup = Employee_Blood_Group.objects.filter(company_id=com.company_id_id,login_id=sid).values('blood_group').distinct()

    return render(request,'company/Employee_Edit_Page.html',{'employe':employe,'allmodules':allmodules,'bloodgroup':bloodgroup,'com':com,'data':loginn})


def employee_update(request,pk):
    employ = Employee.objects.get(id=pk)
    if request.method == 'POST':

        title = request.POST['Title']
        firstname = request.POST['First_Name']
        lastname = request.POST['Last_Name']
        alias = request.POST['Alias']
        joiningdate = request.POST['Joining_Date']
        salarydate = request.POST['Salary_Date']
        
        salary_type = request.POST['Salary_Type']

        if salary_type == 'Fixed':
            amountperhour = 0
            workinghour = 0
            salaryamount = request.POST['Salary_Amount']

        elif salary_type == 'Temporary' :
            amountperhour = 0
            workinghour = 0
            salaryamount = request.POST['Salary_Amount']

        elif salary_type == 'Time Based' :
            amountperhour = request.POST['perhour']
            workinghour = request.POST['workhour']
            salaryamount = request.POST['Salary_Amount']
            

        
        
        employeenumber = request.POST['Employee_Number']
        designation = request.POST['Designation']
        location = request.POST['Location']
        gender = request.POST['Gender']
        image = request.FILES.get('Image', '')
        if len(image) != 0:
            image = request.FILES['Image']
        else:
            image = employ.upload_image
        
        dob = request.POST['DOB']
        blood = request.POST['Blood']
        parent = request.POST['Parent']
        spouse = request.POST['Spouse']
        street = request.POST['street']
        city = request.POST['city']
        state = request.POST['state']
        pincode = request.POST['pincode']
        country = request.POST['country']
        tempStreet = request.POST['tempStreet']
        tempCity = request.POST['tempCity']
        tempState = request.POST['tempState']
        tempPincode = request.POST['tempPincode']
        tempCountry = request.POST['tempCountry']
        
        
        contact = request.POST['Contact_Number']
        emergencycontact = request.POST['Emergency_Contact']
        email = request.POST['Email']
        file = request.FILES.get('File', '')
        if len(file) != 0:
            file = request.FILES['File']
        else:
            file= employ.upload_file

        bankdetails = request.POST['Bank_Details']
        accoutnumber = request.POST['Account_Number']
        ifsc = request.POST['IFSC']
        bankname = request.POST['BankName']
        branchname = request.POST['BranchName']
        transactiontype = request.POST['Transaction_Type']

        

        if request.POST['tds_applicable'] == 'Yes':
            tdsapplicable = request.POST['tds_applicable']
            tdstype = request.POST['TDS_Type']
            
            if tdstype == 'Amount':
                tdsvalue = request.POST['TDS_Amount']
            elif tdstype == 'Percentage':
                tdsvalue = request.POST['TDS_Percentage']
            else:
                tdsvalue = 0
        elif request.POST['tds_applicable'] == 'No':
            tdsvalue = 0
            tdstype = ''
            tdsapplicable = request.POST['tds_applicable']
        else:
            tdsvalue = 0
            tdstype = ''
            tdsapplicable = ''

        
        
        incometax = request.POST['Income_Tax']
        aadhar = request.POST['Aadhar']
        uan = request.POST['UAN']
        pf = request.POST['PF']
        pan = request.POST['PAN']
        pr = request.POST['PR']

        if dob == '':
            age = 2
        else:
            dob2 = date.fromisoformat(dob)
            today = date.today()
            age = int(today.year - dob2.year - ((today.month, today.day) < (dob2.month, dob2.day)))
        
        sid = request.session['s_id']
        emply = Fin_Login_Details.objects.get(id=sid)
        employeee = Employee.objects.get(id=pk)

        

        if emply.User_Type == 'Company':
            companykey =  Fin_Company_Details.objects.get(Login_Id_id=sid)
        elif emply.User_Type == 'Staff':
            staffkey = Fin_Staff_Details.objects.get(Login_Id=sid)
            companykey = Fin_Company_Details.objects.get(id=staffkey.company_id_id)
        else:
            distributorkey = Fin_Distributors_Details.objects.get(login_Id=sid)
            companykey = Fin_Company_Details.objects.get(id=distributorkey.company_id_id)

        emp = Employee.objects.exclude(company_id = companykey.id,id=pk)
        print(emp,'------------------------------------------')
        
        if emp.filter(employee_mail=email,mobile = contact,employee_number=employeenumber,company_id = companykey.id).exists():
            messages.error(request,'user exist')
            return redirect(reverse('employee_edit_page', kwargs={'pk': pk}))

        
        elif emp.filter(mobile = contact,company_id = companykey.id).exists():
            messages.error(request,'phone number exist')
            return redirect(reverse('employee_edit_page', kwargs={'pk': pk}))
        
        elif emp.filter(emergency_contact = emergencycontact,company_id = companykey.id).exists():
            messages.error(request,'phone number exist')
            return redirect(reverse('employee_edit_page', kwargs={'pk': pk}))
        
        elif emp.filter(employee_mail=email,company_id = companykey.id).exists():
            messages.error(request,'email exist')
            return redirect(reverse('employee_edit_page', kwargs={'pk': pk}))
        
        elif emp.filter(employee_number=employeenumber,company_id = companykey.id).exists():
            messages.error(request,'employee id exist')
            return redirect(reverse('employee_edit_page', kwargs={'pk': pk}))
        
        elif incometax != '' and emp.filter(income_tax_number = incometax,company_id = companykey.id).exists():
            messages.error(request,'Income Tax Number exist')
            return redirect(reverse('employee_edit_page', kwargs={'pk': pk}))
        
        elif pf != '' and emp.filter(pf_account_number = pf,company_id = companykey.id).exists():
            messages.error(request,'PF account number exist')
            return redirect(reverse('employee_edit_page', kwargs={'pk': pk}))
        
        elif aadhar != '' and emp.filter(aadhar_number = aadhar,company_id = companykey.id).exists():
            messages.error(request,'Aadhar number exist')
            return redirect(reverse('employee_edit_page', kwargs={'pk': pk}))
        
        elif pan != '' and emp.filter(pan_number = pan,company_id = companykey.id).exists():
            messages.error(request,'PAN number exist')
            return redirect(reverse('employee_edit_page', kwargs={'pk': pk}))
        
        elif uan != '' and emp.filter(universal_account_number = uan,company_id = companykey.id).exists():
            messages.error(request,'Universal account number exist')
            return redirect(reverse('employee_edit_page', kwargs={'pk': pk}))
        
        elif pr != '' and emp.filter(pr_account_number = pr,company_id = companykey.id).exists():
            messages.error(request,'PR account number exist')
            return redirect(reverse('employee_edit_page', kwargs={'pk': pk}))
        
        elif bankdetails.lower() == 'yes':
            if accoutnumber != '' and emp.filter(account_number=accoutnumber,company_id = companykey.id).exists():
                messages.error(request,'Bank account number already exist')
                return redirect(reverse('employee_edit_page', kwargs={'pk': pk}))
            
            else:
        
                employeee.upload_image=image
                employeee.title = title
                employeee.first_name = firstname
                employeee.last_name = lastname
                employeee.alias = alias
                employeee.employee_mail = email
                employeee.employee_number = employeenumber
                employeee.employee_designation = designation
                employeee.employee_current_location = location
                employeee.mobile = contact
                employeee.date_of_joining = joiningdate
                employeee.salary_amount = salaryamount 
                employeee.amount_per_hour = amountperhour 
                employeee.total_working_hours = workinghour
                employeee.gender = gender 
                employeee.date_of_birth = dob 
                employeee.age = age
                employeee.blood_group = blood
                employeee.fathers_name_mothers_name = parent
                employeee.spouse_name = spouse
                employeee.emergency_contact = emergencycontact
                employeee.provide_bank_details = bankdetails
                employeee.account_number = accoutnumber
                employeee.ifsc = ifsc
                employeee.name_of_bank = bankname
                employeee.branch_name = branchname
                employeee.bank_transaction_type = transactiontype
                employeee.tds_applicable = tdsapplicable
                employeee.tds_type = tdstype
                employeee.percentage_amount = tdsvalue
                employeee.pan_number = pan
                employeee.income_tax_number = incometax
                employeee.aadhar_number = aadhar
                employeee.universal_account_number = uan
                employeee.pf_account_number = pf
                employeee.pr_account_number = pr
                employeee.upload_file = file
                employeee.employee_salary_type=salary_type
                employeee.salary_effective_from=salarydate
                employeee.city=city
                employeee.street=street
                employeee.state=state
                employeee.country=country
                employeee.pincode=pincode
                employeee.temporary_city=tempCity
                employeee.temporary_street=tempStreet
                employeee.temporary_state=tempState
                employeee.temporary_pincode=tempPincode
                employeee.temporary_country=tempCountry
                employeee.save()

                history = Employee_History(company_id = employeee.company_id,employee_id = pk,login_id= emply.id,date = date.today(),action = 'Edited')
                history.save()

        
        else:
        
            employeee.upload_image=image
            employeee.title = title
            employeee.first_name = firstname
            employeee.last_name = lastname
            employeee.alias = alias
            employeee.employee_mail = email
            employeee.employee_number = employeenumber
            employeee.employee_designation = designation
            employeee.employee_current_location = location
            employeee.mobile = contact
            employeee.date_of_joining = joiningdate
            employeee.salary_amount = salaryamount 
            employeee.amount_per_hour = amountperhour 
            employeee.total_working_hours = workinghour
            employeee.gender = gender 
            employeee.date_of_birth = dob 
            employeee.age = age
            employeee.blood_group = blood
            employeee.fathers_name_mothers_name = parent
            employeee.spouse_name = spouse
            employeee.emergency_contact = emergencycontact
            employeee.provide_bank_details = bankdetails
            employeee.account_number = accoutnumber
            employeee.ifsc = ifsc
            employeee.name_of_bank = bankname
            employeee.branch_name = branchname
            employeee.bank_transaction_type = transactiontype
            employeee.tds_applicable = tdsapplicable
            employeee.tds_type = tdstype
            employeee.percentage_amount = tdsvalue
            employeee.pan_number = pan
            employeee.income_tax_number = incometax
            employeee.aadhar_number = aadhar
            employeee.universal_account_number = uan
            employeee.pf_account_number = pf
            employeee.pr_account_number = pr
            employeee.upload_file = file
            employeee.employee_salary_type=salary_type
            employeee.salary_effective_from=salarydate
            employeee.city=city
            employeee.street=street
            employeee.state=state
            employeee.country=country
            employeee.pincode=pincode
            employeee.temporary_city=tempCity
            employeee.temporary_street=tempStreet
            employeee.temporary_state=tempState
            employeee.temporary_pincode=tempPincode
            employeee.temporary_country=tempCountry
            employeee.save()

            history = Employee_History(company_id = employeee.company_id,employee_id = pk,login_id= emply.id,date = date.today(),action = 'Edited')
            history.save()
        
        return redirect('employee_overview',pk=employ.id)
    

def employee_profile_email(request,pk):
    
            try:
                if request.method == 'POST':
                    emails_string = request.POST['email_ids']
                    data = Employee.objects.get(id=pk)
                    cmp = Fin_Company_Details.objects.get(id=data.company_id)

                    # Split the string by commas and remove any leading or trailing whitespace
                    emails_list = [email.strip() for email in emails_string.split(',')]
                    email_message = "Here's the requested profile"
                    

                    context = {'cmp': cmp, 'employ': data, 'email_message': email_message}
                    print('context working')

                    template_path = 'company/Employee_Profile_PDF.html'
                    print('tpath working')

                    template = get_template(template_path)
                    print('template working')

                    html = template.render(context)
                    print('html working')

                    result = BytesIO()
                    print('bytes working')

                    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result,path='company/Employee_Profile_PDF.html',base_url=request.build_absolute_uri('/'))
                    print('pisa working')

                    if pdf.err:
                        raise Exception(f"PDF generation error: {pdf.err}")

                    pdf = result.getvalue()
                    print('')
                    filename = f"{data.first_name}_{data.last_name}'s_Profile.pdf"
                    subject = f"{data.first_name}_{data.last_name}'s_Profile"
                    email = EmailMessage(subject, f"Hi, \n{email_message} -of -{cmp.Company_name}. ", from_email=settings.EMAIL_HOST_USER, to=emails_list)
                    email.attach(filename, pdf, "application/pdf")
                    email.send(fail_silently=False)

                    messages.success(request, 'Report has been shared via email successfully..!')
                    return redirect('employee_list')
            except Exception as e:
                messages.error(request, f'Error while sending report: {e}')
                return redirect('employee_list')


def Employee_Profile_PDF(request,pk):
    employ = Employee.objects.get(id=pk)
    return render(request,'company/Employee_Profile_PDF.html',{'employ':employ})
        
def employee_blood_group(request):
    if request.method == 'POST':
        bloodGroup = request.POST.get('bloodGroup', '').upper()
        sid = request.session.get('s_id')
        loginn = Fin_Login_Details.objects.get(id=sid)
        invalid_group = ['A+', 'A-', 'B+', 'O+']

        if loginn.User_Type == 'Company' and bloodGroup not in invalid_group:
            com = Fin_Company_Details.objects.get(Login_Id=sid)
            
            allmodules = Fin_Modules_List.objects.get(company_id=com.id)
            group = Employee_Blood_Group(blood_group=bloodGroup, company_id=com.id, login_id=sid)
            group.save()
            bloodgroup = Employee_Blood_Group.objects.filter(company_id=com.id,login_id=sid).values('blood_group').distinct()
            return JsonResponse({'success': True,'bloodgroup': list(bloodgroup)})

        elif loginn.User_Type == 'Staff' and bloodGroup not in invalid_group:
            com = Fin_Staff_Details.objects.get(Login_Id = sid)
            allmodules = Fin_Modules_List.objects.get(company_id=com.company_id_id)
            group = Employee_Blood_Group(blood_group=bloodGroup, company_id=com.company_id_id, login_id=sid)
            group.save()
            bloodgroup = Employee_Blood_Group.objects.filter(company_id=com.company_id_id,login_id=sid).values('blood_group').distinct()
            return JsonResponse({'success': True,'bloodgroup': list(bloodgroup)})

    return JsonResponse({'success': False, 'error': 'Invalid blood group or user type'})
    
def bloodgroup_data(request):
    sid = request.session.get('s_id')
    loginn = Fin_Login_Details.objects.get(id=sid)
    
    if loginn.User_Type == 'Company' :
            com = Fin_Company_Details.objects.get(Login_Id=sid)
            
            bloodgroup = Employee_Blood_Group.objects.filter(company_id=com.id,login_id=sid).values('blood_group').distinct()
            return JsonResponse({'success': True,'bloodgroup': list(bloodgroup)})

    elif loginn.User_Type == 'Staff' :
            com = Fin_Staff_Details.objects.get(Login_Id = sid)
            bloodgroup = Employee_Blood_Group.objects.filter(company_id=com.company_id_id,login_id=sid).values('blood_group').distinct()
            return JsonResponse({'success': True,'bloodgroup': list(bloodgroup)})

    else:
        return JsonResponse({'success': False,'bloodgroup': list(bloodgroup)})
# holiday section--------------------------------------------------------------------------------------------------------------------------
    
def holiday_list(request):
    sid = request.session['s_id']
    loginn = Fin_Login_Details.objects.get(id=sid)
    if loginn.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        # holiday = Holiday.objects.filter(company_id=com.id).annotate(month=ExtractMonth('start_date'),year=ExtractYear('start_date')).values('month','year').annotate(total_holiday=Sum('holiday_days')).order_by('year','month')
        holiday = Holiday.objects.filter(company_id=com.id).annotate(month=ExtractMonth('start_date'), year=ExtractYear('start_date')).values('month', 'year').annotate(total_holiday=Cast(Sum(F('holiday_days')),IntegerField())).order_by('year', 'month')
        
        
    else:
        com = Fin_Staff_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
        holiday = Holiday.objects.filter(company_id=com.company_id_id).annotate(month=ExtractMonth('start_date'), year=ExtractYear('start_date')).values('month', 'year').annotate(total_holiday=Cast(Sum(F('holiday_days')),IntegerField())).order_by('year', 'month')
    
    
    return render(request,'company/Holiday_List.html',{'holiday':holiday,'allmodules':allmodules,'com':com,'data':loginn})
 
def holiday_create_page(request):
    sid = request.session['s_id']
    loginn = Fin_Login_Details.objects.get(id=sid)
    if loginn.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        
    elif loginn.User_Type == 'Staff' :
        com = Fin_Staff_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
    return render(request,'company/Holiday_Create_Page.html',{'allmodules':allmodules,'com':com,'data':loginn})

def holiday_add(request):
    if request.method == 'POST':
        startdate = request.POST['date1']
        enddate = request.POST['date2']
        title = request.POST['title']

        start_date1 = datetime.strptime(startdate, '%Y-%m-%d').date()
        end_date1 = datetime.strptime(enddate, '%Y-%m-%d').date()
        day_s = end_date1 - start_date1 + timedelta(days=1)
        
    sid = request.session['s_id']
    loginn = Fin_Login_Details.objects.get(id=sid)
    if loginn.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        holiday_check = Holiday.objects.filter(start_date=startdate,end_date=enddate,company_id=com.id)
            
    elif loginn.User_Type == 'Staff' :
        com = Fin_Staff_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
        holiday_check = Holiday.objects.filter(start_date=startdate,end_date=enddate,company_id=com.company_id_id)
        
    if holiday_check.exists():
        messages.error(request,' Dates are already listed as holiday')
        return render(request,'company/Holiday_Create_Page.html',{'allmodules':allmodules,'com':com,'data':loginn})

    # uncomment if you want to check whether the holidays would overlap
    # elif Holiday.objects.filter(Q(start_date__lte=startdate) & Q(end_date__gte=startdate)).exists() or Holiday.objects.filter(Q(start_date__lte=enddate) & Q(end_date__gte=enddate)).exists():
    #     messages.error(request,'Some dates are already listed as holiday')
    #     sid = request.session['s_id']
    #     loginn = Fin_Login_Details.objects.get(id=sid)
    #     if loginn.User_Type == 'Company':
    #         com = Fin_Company_Details.objects.get(Login_Id = sid)# 
    #         allmodules = Fin_Modules_List.objects.get(company_id = com.id)
            
    #     elif loginn.User_Type == 'Staff' :
    #         com = Fin_Staff_Details.objects.get(Login_Id = sid)# 
    #         allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
    #     return render(request,'company/Holiday_Create_Page.html',{'allmodules':allmodules})
    
    else:
        sid = request.session['s_id']
        loginn = Fin_Login_Details.objects.get(id=sid)
        if loginn.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = sid)
            allmodules = Fin_Modules_List.objects.get(company_id = com.id)
            holiday = Holiday(start_date=startdate,end_date=enddate,login_id=sid,holiday_name=title,company_id=com.id,holiday_days=day_s)
            holiday.save()
            history = Holiday_History(company_id = com.id,login_id=sid,holiday_id = holiday.id,date = date.today(),action = 'Created',start_date = startdate,end_date = enddate,holiday_name=title)
            history.save()
            holidayss = Holiday.objects.filter(company_id=com.id).annotate(month=ExtractMonth('start_date'), year=ExtractYear('start_date')).values('month', 'year').annotate(total_holiday=Cast(Sum(F('holiday_days')),IntegerField())).order_by('year', 'month')

        else:
            com = Fin_Staff_Details.objects.get(Login_Id = sid)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
            holiday = Holiday(start_date=startdate,end_date=enddate,holiday_name=title,login_id=sid,company_id=com.company_id_id,holiday_days=day_s)
            holiday.save()
            history = Holiday_History(company_id = com.id,login_id=sid,holiday_id = holiday.id,date = date.today(),action = 'Created',start_date = startdate,end_date = enddate,holiday_name=title)
            history.save()
            holidayss = Holiday.objects.filter(company_id=com.company_id_id).annotate(month=ExtractMonth('start_date'), year=ExtractYear('start_date')).values('month', 'year').annotate(total_holiday=Cast(Sum(F('holiday_days')),IntegerField())).order_by('year', 'month')
            
        return render(request,'company/Holiday_List.html',{'allmodules':allmodules,'holiday':holidayss,'com':com,'data':loginn})
        
    
def holiday_calendar_view(request,mn,yr):
    month = int(mn)-1
    year = int(yr)
    
    sid = request.session['s_id']
    loginn = Fin_Login_Details.objects.get(id=sid)
    if loginn.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        events = Holiday.objects.filter(start_date__month=mn,start_date__year=year,company_id=com.id)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        comments = Holiday_Comment.objects.filter(month=mn,year=year,company_id=com.id)
        for index, comment in enumerate(comments):
            comment.index = index + 1
        
    elif loginn.User_Type == 'Staff' :
        com = Fin_Staff_Details.objects.get(Login_Id = sid)
        events = Holiday.objects.filter(start_date__month=mn,start_date__year=year,company_id=com.company_id_id)
        allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
        comments = Holiday_Comment.objects.filter(month=mn,year=year,company_id=com.company_id_id)
        for index, comment in enumerate(comments):
            comment.index = index + 1

    return render(request, 'company/Holiday_Calendar.html', {'comments':comments,'events': events,'allmodules':allmodules,'year':year,'month':month,'com':com,'data':loginn})

def holiday_delete(request, pk):
    sid = request.session['s_id']
    loginn = Fin_Login_Details.objects.get(id=sid)
    if loginn.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)

        if request.method == 'POST':
            ogMonth = int(request.POST['month'])
            year = int(request.POST['year'])
            month = ogMonth + 1
            holiday = Holiday.objects.get(id=pk)
            holiday.delete()
            events = Holiday.objects.filter(start_date__month=month,start_date__year=year,company_id=com.id)
            if events.exists():
                return render(request, 'company/Holiday_Calendar.html', {'events': events,'allmodules':allmodules,'year':year,'month':ogMonth,'com':com,'data':loginn})
            else:
                return redirect('holiday_list')
        
    elif loginn.User_Type == 'Staff' :
        com = Fin_Staff_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)

        if request.method == 'POST':
            ogMonth = int(request.POST['month'])
            year = int(request.POST['year'])
            month = ogMonth + 1
            holiday = Holiday.objects.get(id=pk)
            holiday.delete()
            events = Holiday.objects.filter(start_date__month=month,start_date__year=year,company_id = com.company_id_id)
            if events.exists():
                return render(request, 'company/Holiday_Calendar.html', {'events': events,'allmodules':allmodules,'year':year,'month':ogMonth,'com':com,'data':loginn})
            else:
                return redirect('holiday_list')


def holiday_edit_page(request,pk,mn,yr):
    holiday = Holiday.objects.get(id=pk)
    sid = request.session['s_id']
    loginn = Fin_Login_Details.objects.get(id=sid)
    if loginn.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        
    elif loginn.User_Type == 'Staff' :
        com = Fin_Staff_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
    return render(request,'company/Holiday_Edit_Page.html',{'holiday':holiday,'allmodules':allmodules,'com':com,'data':loginn,'year':yr,'month':mn})


def holiday_update(request,pk,mn,yr):
    mon = mn+1
    holiday = Holiday.objects.get(id=pk)
    if request.method == 'POST':
        startdate = request.POST['date1']
        enddate = request.POST['date2']
        title = request.POST['title']

        start_date1 = datetime.strptime(startdate, '%Y-%m-%d').date()
        end_date1 = datetime.strptime(enddate, '%Y-%m-%d').date()
        day_s = end_date1 - start_date1 + timedelta(days=1)

    sid = request.session['s_id']
    loginn = Fin_Login_Details.objects.get(id=sid)
    if loginn.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = sid)
            companyID = com.id
            allmodules = Fin_Modules_List.objects.get(company_id = com.id)
            
    elif loginn.User_Type == 'Staff' :
            com = Fin_Staff_Details.objects.get(Login_Id = sid)
            companyID = com.company_id_id
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
        
    holi = Holiday.objects.filter(start_date=startdate,end_date=enddate,company_id=companyID)
    if holi.exclude(id=pk).exists():
            error = 'yes'
            messages.error(request,'Some dates are already listed as holiday')
            sid = request.session['s_id']
            loginn = Fin_Login_Details.objects.get(id=sid)
            if loginn.User_Type == 'Company':
                com = Fin_Company_Details.objects.get(Login_Id = sid)
                allmodules = Fin_Modules_List.objects.get(company_id = com.id)
                
            elif loginn.User_Type == 'Staff' :
                com = Fin_Staff_Details.objects.get(Login_Id = sid)
                allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
            return render(request,'company/Holiday_Edit_Page.html',{'holiday':holiday,'allmodules':allmodules,'com':com,'data':loginn})
        
    else:
            sid = request.session['s_id']
            loginn = Fin_Login_Details.objects.get(id=sid)
            if loginn.User_Type == 'Company':
                com = Fin_Company_Details.objects.get(Login_Id = sid)
                allmodules = Fin_Modules_List.objects.get(company_id = com.id)
                
                holiday.start_date = startdate
                holiday.end_date = enddate
                holiday.holiday_name=title
                holiday.login_id=sid
                holiday.company_id=com.id
                holiday.holiday_days=day_s
                holiday.save()
                history = Holiday_History(company_id = com.id,login_id=sid,holiday_id = holiday.id,date = date.today(),action = 'Edited',start_date = startdate,end_date = enddate,holiday_name=title)
                history.save()  
                
                holida_y = Holiday.objects.filter(company_id=com.id).annotate(month=ExtractMonth('start_date'), year=ExtractYear('start_date')).values('month', 'year').annotate(total_holiday=Cast(Sum(F('holiday_days')),IntegerField())).order_by('year', 'month')

            else:
                com = Fin_Staff_Details.objects.get(Login_Id = sid)
                allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
                
                holiday.start_date = startdate
                holiday.end_date = enddate
                holiday.holiday_name=title
                holiday.login_id=sid
                holiday.company_id=com.company_id_id
                holiday.holiday_days=day_s
                holiday.save()
                history = Holiday_History(company_id = com.company_id_id,login_id=sid,holiday_id = holiday.id,date = date.today(),action = 'Edited',start_date = startdate,end_date = enddate,holiday_name=title)
                history.save()  

                holida_y = Holiday.objects.filter(company_id=com.company_id_id).annotate(month=ExtractMonth('start_date'), year=ExtractYear('start_date')).values('month', 'year').annotate(total_holiday=Cast(Sum(F('holiday_days')),IntegerField())).order_by('year', 'month')

    return redirect('holiday_calendar_view', mn=mon, yr=yr)
    # return render(request,'company/Holiday_List.html',{'holiday':holida_y,'allmodules':allmodules,'com':com,'data':loginn})


def holiday_comment(request,mn,yr):
    Month = mn+1
    
    todayDate = date.today()
    sid = request.session['s_id']
    log_in = Fin_Login_Details.objects.get(id=sid)
    loginID = log_in.id
    
    if log_in.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        
        if request.method == 'POST':
            comments = request.POST['comment']  
            holidayComment = Holiday_Comment(month = Month, year = yr,company_id=com.id,login_id=loginID,comment=comments,date=todayDate)
            holidayComment.save()
            
    elif log_in.User_Type == 'Staff' :
        com = Fin_Staff_Details.objects.get(Login_Id = sid)
        
        if request.method == 'POST':
            comments = request.POST['comment']  
            holidayComment = Holiday_Comment(month = Month, year = yr,company_id=com.company_id_id,login_id=loginID,comment=comments,date=todayDate)
            holidayComment.save()
    
    redirect_url = reverse('holiday_calendar_view', args=[Month, yr])
    return redirect(redirect_url)
    
def holiday_comment_delete(request, pk,mn,yr):
    holiday = Holiday_Comment.objects.get(id=pk)
    holiday.delete()
    redirect_url = reverse('holiday_calendar_view', args=[mn, yr])
    return redirect(redirect_url)

def holiday_history(request,month,year):
        mn = month + 1
        
        startdate = datetime(year, mn, 1)
        if mn == 12:
            enddate = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            enddate = datetime(year, mn + 1, 1) - timedelta(days=1)

        print(startdate,enddate,'----------------------------------------------------')
        sid = request.session['s_id']
        loginn = Fin_Login_Details.objects.get(id=sid)
        if loginn.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = sid)
            allmodules = Fin_Modules_List.objects.get(company_id = com.id)
            history = Holiday_History.objects.filter(company_id=com.id,start_date__gt = startdate,end_date__lt = enddate)
            
        elif loginn.User_Type == 'Staff' :
            com = Fin_Staff_Details.objects.get(Login_Id = sid)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
            history = Holiday_History.objects.filter(company_id=com.company_id_id,start_date__gt = startdate,end_date__lt = enddate)
        
        
        return render(request,'company/Holiday_History.html',{'history':history,'allmodules':allmodules,'com':com,'data':loginn,'month':mn,'year':year})
        
def employee_comment_delete(request,pk,id):
    employee_comment = Employee_Comment.objects.get(id=pk)
    employee_comment.delete()
    redirect_url = reverse('employee_overview', args=[id])
    return redirect(redirect_url)
# harikrishnan end ---------------

# ---------------------------Start Banking------------------------------------ 

def Fin_banking_listout(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        all_bankings = Fin_Banking.objects.filter(company = company)
        print(all_bankings)

        context = {
            'login_det':login_det,
            'com':com,
            'allmodules':allmodules,
            'all_bankings':all_bankings
        }
        return render(request,'company/banking/Fin_banking_listout.html',context)
    else:
       return redirect('/')  

def Fin_banking_sort_by_name(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        all_bankings = Fin_Banking.objects.filter(company = company).order_by('bank_name')
        print(all_bankings)

        context = {
            'login_det':login_det,
            'com':com,
            'allmodules':allmodules,
            'all_bankings':all_bankings
        }
        return render(request,'company/banking/Fin_banking_listout.html',context)
    else:
       return redirect('/')  
    
def Fin_banking_sort_by_balance(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        all_bankings = Fin_Banking.objects.filter(company = company).order_by('bank_name')
        print(all_bankings)

        context = {
            'login_det':login_det,
            'com':com,
            'allmodules':allmodules,
            'all_bankings':all_bankings
        }
        return render(request,'company/banking/Fin_banking_listout.html',context)
    else:
       return redirect('/')

def Fin_banking_filter_active(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        all_bankings = Fin_Banking.objects.filter(company = company,bank_status = 'Active')
        print(all_bankings)

        context = {
            'login_det':login_det,
            'com':com,
            'allmodules':allmodules,
            'all_bankings':all_bankings
        }
        return render(request,'company/banking/Fin_banking_listout.html',context)
    else:
       return redirect('/') 

def Fin_banking_filter_inactive(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        all_bankings = Fin_Banking.objects.filter(company = company,bank_status = 'Inactive')
        print(all_bankings)

        context = {
            'login_det':login_det,
            'com':com,
            'allmodules':allmodules,
            'all_bankings':all_bankings
        }
        return render(request,'company/banking/Fin_banking_listout.html',context)
    else:
       return redirect('/') 

def Fin_create_bank(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')


        context = {
                'login_det':login_det,
                'com':com,
                'allmodules':allmodules
            }
        return render(request,'company/banking/Fin_create_bank.html',context)
    else:
       return redirect('/')  

def Fin_banking_check_account_number(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id


        if request.method == 'GET':
            bank_name = request.GET.get('bank_name', '')
            account_number = request.GET.get('account_number', '')

            print(account_number)
            # Check if the account number exists for the given bank
            exists = Fin_Banking.objects.filter( account_number=account_number,company = company ).exists()

            # Return a JSON response indicating whether the account number exists
            return JsonResponse({'exists': exists})

    # Handle other HTTP methods if necessary
    return JsonResponse({'exists': False})  # Default to 'False' if the request is not a GET

def Fin_create_bank_account(request):
     if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')


        if request.method == 'POST':
            bname = request.POST.get('bname')
            ifsc = request.POST.get('ifsc')
            branch = request.POST.get('branch')
            opening_balance = request.POST.get('Opening')
            date = request.POST.get('date')
            opening_blnc_type = request.POST.get('op_type')
            acc_num = request.POST.get('acc_num')
            
            if opening_blnc_type == 'CREDIT':
                opening_balance = 0 -int(opening_balance)
            
            bank = Fin_Banking(
                login_details = login_det,
                company = company,
                bank_name=bname, 
                ifsc_code=ifsc,
                branch_name=branch, 
                opening_balance=opening_balance, 
                opening_balance_type = opening_blnc_type,
                date=date,
                current_balance=opening_balance,
                account_number=acc_num,
                bank_status = 'Active')
            bank.save()

            banking_history = Fin_BankingHistory(
                login_details = login_det,
                company = company,
                banking = bank,
                action = 'Created'
            )
            banking_history.save()
            
            transaction=Fin_BankTransactions(
                login_details = login_det,
                company = company,
                banking = bank,
                amount = opening_balance,
                adjustment_date = date,
                transaction_type = "Opening Balance",
                from_type = '',
                to_type = '',
                current_balance = opening_balance
                
            )
            transaction.save()

            transaction_history = Fin_BankTransactionHistory(
                login_details = login_det,
                company = company,
                bank_transaction = transaction,
                action = 'Created'
            )
            transaction_history.save()

            
            return redirect('Fin_banking_listout')

def Fin_view_bank(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')
        
        bank = Fin_Banking.objects.get(id=id)
        bank_list = Fin_Banking.objects.filter(company=company)
        trans = Fin_BankTransactions.objects.filter(banking_id=id) 
        comments = Fin_BankingComments.objects.filter(banking_id=id) 
        last_history = Fin_BankingHistory.objects.filter(banking_id=id).last()
        
        context = {
                'login_det':login_det,
                'com':com,
                'allmodules':allmodules,
                "bank":bank,
                'bl':bank_list,
                'trans':trans,
                'comments':comments,
                'last_history':last_history,
            }   

        return render(request,'company/banking/Fin_view_bank.html',context)

def Fin_bank_to_cash(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        bank=Fin_Banking.objects.get(id = id)
        all_banks = Fin_Banking.objects.filter(company = company)

        context = {
                'login_det':login_det,
                'com':com,
                'allmodules':allmodules,
                'bank':bank,
                'all_banks':all_banks,
               
            }  
       
        return render(request,'company/banking/Fin_bank_to_cash.html',context)
    
def Fin_save_bankTocash(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        if request.method == 'POST':
            f_bank = request.POST.get('bank')
            amount = int(request.POST.get('amount'))
            adj_date = request.POST.get('adjdate')
            desc = request.POST.get('desc')

            

            bank = Fin_Banking.objects.get(id=f_bank)
            bank.current_balance -= amount
            bank.save()
            
            transaction = Fin_BankTransactions(
                login_details = login_det,
                company = company,
                banking = bank,
                from_type = '',
                to_type='',
                amount=amount,
                description=desc,
                adjustment_date=adj_date,
                transaction_type='Cash Withdraw',
                current_balance= bank.current_balance               
            )
            transaction.save()
            transaction_history = Fin_BankTransactionHistory(
                login_details = login_det,
                company = company,
                bank_transaction = transaction,
                action = 'Created'
            )
            transaction_history.save()
            
        return redirect('Fin_view_bank',bank.id)
    
def Fin_cash_to_bank(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        bank=Fin_Banking.objects.get(id = id)
        all_banks = Fin_Banking.objects.filter(company = company)

        context = {
                'login_det':login_det,
                'com':com,
                'allmodules':allmodules,
                'bank':bank,
                'all_banks':all_banks,
               
            }  
       
        return render(request,'company/banking/Fin_cash_to_bank.html',context)
    
def Fin_save_cashTobank(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        if request.method == 'POST':
            t_bank = request.POST.get('bank')
            amount = int(request.POST.get('amount'))
            adj_date = request.POST.get('adjdate')
            desc = request.POST.get('desc')

            

            bank = Fin_Banking.objects.get(id=t_bank)
            bank.current_balance += amount
            bank.save()
            
            transaction = Fin_BankTransactions(
                login_details = login_det,
                company = company,
                banking = bank,
                from_type = '',
                to_type='',
                amount=amount,
                description=desc,
                adjustment_date=adj_date,
                transaction_type='Cash Deposit', 
                current_balance= bank.current_balance                 
            )
            transaction.save()
            transaction_history = Fin_BankTransactionHistory(
                login_details = login_det,
                company = company,
                bank_transaction = transaction,
                action = 'Created'
            )
            transaction_history.save()
            
        return redirect('Fin_view_bank',bank.id)   
    
def Fin_bank_to_bank(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        bank=Fin_Banking.objects.get(id = id)
        all_banks = Fin_Banking.objects.filter(company = company)

        context = {
                'login_det':login_det,
                'com':com,
                'allmodules':allmodules,
                'bank':bank,
                'all_banks':all_banks,
               
            }  
       
        return render(request,'company/banking/Fin_bank_to_bank.html',context)
    
def Fin_save_bankTobank(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        current_bank = Fin_Banking.objects.get(id=id)

        if request.method == 'POST':
            print('hi')
            f_bank = request.POST.get('fbank')
            print(f_bank)
            t_bank = request.POST.get('tbank')
            amount = int(request.POST.get('amount'))
            adj_date = request.POST.get('adjdate')
            desc = request.POST.get('desc')


            from_bank = Fin_Banking.objects.get(id=f_bank)
            print(from_bank)
            to_bank = Fin_Banking.objects.get(id=t_bank)
            to_bank.current_balance += amount
            from_bank.current_balance -= amount
            to_bank.save()
            from_bank.save()
            

            transaction_withdraw = Fin_BankTransactions(
                login_details = login_det,
                company = company,
                banking = from_bank,
                from_type = 'From :' + from_bank.bank_name,
                to_type='To :' + to_bank.bank_name,
                amount=amount,
                description=desc,
                adjustment_date=adj_date,
                transaction_type='From Bank Transfer', 
                current_balance= from_bank.current_balance,
                               
            )
            transaction_withdraw.save()
            transaction_history = Fin_BankTransactionHistory(
                login_details = login_det,
                company = company,
                bank_transaction = transaction_withdraw,
                action = 'Created'
            )
            transaction_history.save()

            transaction_deposit = Fin_BankTransactions(
                login_details = login_det,
                company = company,
                banking = to_bank,
                from_type = 'From :' + from_bank.bank_name,
                to_type='To :' + to_bank.bank_name,
                amount=amount,
                description=desc,
                adjustment_date=adj_date,
                transaction_type='To Bank Transfer', 
                current_balance= to_bank.current_balance,
            )
            transaction_deposit.save()
            transaction_history = Fin_BankTransactionHistory(
                login_details = login_det,
                company = company,
                bank_transaction = transaction_deposit,
                action = 'Created'
            )
            transaction_history.save()

            transaction_withdraw.bank_to_bank = transaction_deposit.id
            transaction_deposit.bank_to_bank = transaction_withdraw.id
            transaction_withdraw.save()
            transaction_deposit.save()
            
        return redirect('Fin_view_bank',current_bank.id)   
    
def Fin_bank_adjust(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        bank=Fin_Banking.objects.get(id = id)
        all_banks = Fin_Banking.objects.filter(company = company)

        context = {
                'login_det':login_det,
                'com':com,
                'allmodules':allmodules,
                'bank':bank,
                'all_banks':all_banks,
               
            }  
       
        return render(request,'company/banking/Fin_bank_adjust.html',context)

def Fin_save_bank_adjust(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        if request.method == 'POST':
            t_bank = request.POST.get('bank')
            amount = int(request.POST.get('amount'))
            adj_date = request.POST.get('adjdate')
            adj_type = request.POST.get('typ')
            desc = request.POST.get('desc')

            bank = Fin_Banking.objects.get(id=t_bank)

            if adj_type == 'Increase Balance':
                bank.current_balance += amount
                bank.save()
               
            else:
                bank.current_balance -= amount
                bank.save()
                
            
            transaction = Fin_BankTransactions(
                login_details = login_det,
                company = company,
                banking = bank,
                from_type = '',
                to_type='',
                amount=amount,
                description=desc,
                adjustment_date=adj_date,
                transaction_type='Adjust bank Balance', 
                current_balance= bank.current_balance,     
                      
            )
            transaction.save()


            if adj_type == 'Increase Balance':
              
                transaction.adjustment_type = 'Increase Balance'
                transaction.save()
            else:
               
                transaction.adjustment_type = 'Reduce Balance'
                transaction.save()

            
            transaction_history = Fin_BankTransactionHistory(
                login_details = login_det,
                company = company,
                bank_transaction = transaction,
                action = 'Created'
            )
            transaction_history.save()
            
        return redirect('Fin_view_bank',bank.id) 

def Fin_edit_bank(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        bank = Fin_Banking.objects.get(id=id)

        context = {
                'login_det':login_det,
                'com':com,
                'allmodules':allmodules,
                'bank':bank
            }
        return render(request,'company/banking/Fin_edit_bank.html',context)
    else:
       return redirect('/')   

def Fin_edit_bank_account(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        bank = Fin_Banking.objects.get(id = id)
        old_op_blnc = int(bank.opening_balance)
        transactions = Fin_BankTransactions.objects.filter(banking=bank)
        transactions_count = Fin_BankTransactions.objects.filter(banking=bank).count()

        
        if request.method == 'POST':
            bname = request.POST.get('bname')
            ifsc = request.POST.get('ifsc')
            branch = request.POST.get('branch')
            opening_balance = request.POST.get('Opening')
            date = request.POST.get('date')
            opening_blnc_type = request.POST.get('op_type')
            acc_num = request.POST.get('acc_num')
            
            if opening_blnc_type == 'CREDIT':
                opening_balance = 0 -int(opening_balance)

            if old_op_blnc == int(opening_balance):
                print('same')
                bank.login_details = login_det
                bank.company = company
                bank.bank_name=bname
                bank.ifsc_code=ifsc
                bank.branch_name=branch
                bank.opening_balance=opening_balance 
                bank.opening_balance_type = opening_blnc_type
                bank.date=date
                bank.current_balance=opening_balance
                bank.account_number=acc_num
                bank.save()

                banking_history = Fin_BankingHistory(
                    login_details = login_det,
                    company = company,
                    banking = bank,
                    action = 'Updated'
                )
                banking_history.save()

            elif old_op_blnc < int(opening_balance): 

                print('increase')
                increased_amount =  int(opening_balance) - old_op_blnc 
                print('increased_amount')
                bank.login_details = login_det
                bank.company = company
                bank.bank_name=bname
                bank.ifsc_code=ifsc
                bank.branch_name=branch
                bank.opening_balance=opening_balance 
                bank.opening_balance_type = opening_blnc_type
                bank.date=date
                bank.current_balance += int(increased_amount)
                bank.account_number=acc_num
                bank.save()

                banking_history = Fin_BankingHistory(
                    login_details = login_det,
                    company = company,
                    banking = bank,
                    action = 'Updated'
                )
                banking_history.save() 

                for t in transactions:
                    print('for')
                    print(t)
                    t.login_details_id = login_det.id
                    t.company_id = company.id
                    t.banking_id = bank.id
                    if t.transaction_type == "Opening Balance":
                        t.amount = t.amount + int(increased_amount)
                    t.current_balance = t.current_balance + int(increased_amount)
                    t.save()

                transaction_history = Fin_BankTransactionHistory(
                    login_details = login_det,
                    company = company,
                    bank_transaction = t,
                    action = 'Updated'
                )
                transaction_history.save() 

            elif old_op_blnc > int(opening_balance): 

                print('decrease')  
                decreased_amount =  old_op_blnc - int(opening_balance)
                print('decreased_amount')
                bank.login_details = login_det
                bank.company = company
                bank.bank_name=bname
                bank.ifsc_code=ifsc
                bank.branch_name=branch
                bank.opening_balance=opening_balance 
                bank.opening_balance_type = opening_blnc_type
                bank.date=date
                bank.current_balance = bank.current_balance - int(decreased_amount)
                bank.account_number=acc_num
                bank.save()

                banking_history = Fin_BankingHistory(
                    login_details = login_det,
                    company = company,
                    banking = bank,
                    action = 'Updated'
                )
                banking_history.save() 

                for t in transactions:
                    print(t)
                    t.login_details_id = login_det.id
                    t.company_id = company.id
                    t.banking_id = bank.id
                    if t.transaction_type == "Opening Balance":
                        t.amount = t.amount - int(decreased_amount)
                    t.current_balance = t.current_balance - int(decreased_amount)
                    t.save()

                transaction_history = Fin_BankTransactionHistory(
                    login_details = login_det,
                    company = company,
                    bank_transaction = t,
                    action = 'Updated'
                )
                transaction_history.save()       
                        
    return redirect('Fin_view_bank',bank.id)



def Fin_change_bank_status(request,id):
   
    bank = Fin_Banking.objects.get(id =id)
    
    if bank.bank_status == "Active":
        bank.bank_status = "Inactive"
    else:
        bank.bank_status = "Active"
    bank.save()

    return redirect('Fin_view_bank',id=id)

def Fin_delete_bank(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        all_bankings = Fin_Banking.objects.filter(company = company)
   
        bank = Fin_Banking.objects.get(id =id)
        
        transactions_count = Fin_BankTransactions.objects.filter(banking = bank).count()
        print(transactions_count) 

        if transactions_count == 0:
            try:
                bank_history = Fin_BankingHistory.objects.filter(banking = bank)
                bank_history.delete()
                bank.delete()
            except:
                bank.delete()
            
            messages.success(request, 'Bank has been deleted successfully.')

            return redirect('Fin_banking_listout')

        elif transactions_count == 1:
            transaction = Fin_BankTransactions.objects.get(banking = bank)
            transaction_history = Fin_BankTransactionHistory.objects.filter(bank_transaction = transaction)
            bank_history = Fin_BankingHistory.objects.filter(banking = bank)
            transaction_history.delete()
            transaction.delete()
            bank_history.delete()
            bank.delete()

            messages.success(request, 'Bank has been deleted successfully.')

            return redirect('Fin_banking_listout')

        elif transactions_count > 1:
            bank.bank_status = "Inactive"
            bank.save()

            messages.success(request, 'Bank already have some transactions so the status has been changed to Inactive')

            return redirect('Fin_view_bank',id=id)


def Fin_banking_add_file(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        bank = Fin_Banking.objects.get(id =id)

        if request.method == 'POST':
            
            if len(request.FILES) != 0:
               file = request.FILES['file']

               attachment = Fin_BankingAttachments(
                   login_details = login_det,
                   company = company,
                   banking = bank,
                   file = file
               )
               attachment.save()

            messages.success(request, 'File has been saved successfully.')
            return redirect('Fin_view_bank',id=id)

def Fin_banking_add_comment(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        bank = Fin_Banking.objects.get(id =id)

        if request.method == 'POST':
            comment_text = request.POST.get('comment_text', '')

            if comment_text and bank:
                comment = Fin_BankingComments.objects.create(
                    login_details = login_det,
                    company = company,
                    banking = bank,
                    comment=comment_text)
                comment.save()

        messages.success(request, 'Comment has been saved successfully.')
        return redirect('Fin_view_bank',id=id)

def Fin_banking_delete_comment(request,id):

    if request.method == 'GET':

        comment = Fin_BankingComments.objects.get(id=id)
        bank = comment.banking

        comment.delete()

    messages.success(request, 'Comment has been deleted..')
    return redirect('Fin_view_bank',id=bank.id)


def Fin_banking_history(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        bank = Fin_Banking.objects.get(id =id)
        bank_history = Fin_BankingHistory.objects.filter(banking = bank)

        context = {
                'login_det':login_det,
                'com':com,
                'allmodules':allmodules,
                'bank_history':bank_history,
                'bank':bank
            }
        return render(request,'company/banking/Fin_banking_history.html',context)
    


def Fin_shareBankingStatementToEmail(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        try:
            if request.method == 'POST':
                emails_string = request.POST['email_ids']

    
                emails_list = [email.strip() for email in emails_string.split(',')]
                email_message = request.POST['email_message']
                print(emails_list)

               
                bank = Fin_Banking.objects.get(id=id)
                transactions = Fin_BankTransactions.objects.filter(banking=bank)
                        
                context = {'bank':bank, 
                           'company':company,
                           'trans':transactions
                           }
                template_path = 'company/banking/Fin_statement_template_to_mail.html'
                template = get_template(template_path)

                html  = template.render(context)
                result = BytesIO()
                pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
                pdf = result.getvalue()
                filename = f'BANKING - {bank.id}.pdf'
                subject = f"BANKING - {bank.id}"
                email = EmailMessage(subject, f"Hi,\nPlease find the attached STATEMENT - File-{bank.id}. \n{email_message}\n\n--\nRegards,\n{company.Company_name}\n{company.Address}\n{company.State} - {company.Country}\n{company.Contact}", from_email=settings.EMAIL_HOST_USER, to=emails_list)
                email.attach(filename, pdf, "application/pdf")
                email.send(fail_silently=False)

                msg = messages.success(request, 'Statement has been shared via email successfully..!')
                return redirect('Fin_view_bank',id=bank.id)
        except Exception as e:
            print(e)
            messages.error(request, f'{e}')
            return redirect('Fin_view_bank',id=bank.id)

def Fin_render_pdfstatment_view(request,id):
    
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        bank = Fin_Banking.objects.get(id=id)
        trans = Fin_BankTransactions.objects.filter(banking=bank)
        template_path = 'company/banking/Fin_banking_statement_pdf.html'
        context ={
            'bank':bank,
            'company':company,
            'trans':trans,
            
        }
        fname=bank.bank_name
    
        # Create a Django response object, and specify content_type as pdftemp_creditnote
        response = HttpResponse(content_type='application/pdf')
        #response['Content-Disposition'] = 'attachment; filename="certificate.pdf"'
        response['Content-Disposition'] =f'attachment; filename= {fname}.pdf'
        # find the template and render it.
        template = get_template(template_path)
        html = template.render(context)

        # create a pdf
        pisa_status = pisa.CreatePDF(
        html, dest=response)
        


        # if error then show some funy view
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
#-------------------------------------------------------------------------- end of banking----------------------------------------------------------------


def employee_overview_print(request,pk):
    employ = Employee.objects.get(id = pk)
    comments = Employee_Comment.objects.filter(employee_id = pk,company_id=employ.company_id)
    return render(request,'company/Employee_Print_Page.html',{'comments':comments ,'employ':employ})
    
    
def Fin_createPriceList(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        if request.method == 'POST':
            name = request.POST['name']
            type = request.POST['type']
            itemRate = request.POST['item_rate']
            description = request.POST['description']
            upOrDown = request.POST['up_or_down']
            percent = request.POST['percentage']
            roundOff = request.POST['round_off']
            currency = request.POST['currency']

            if Fin_Price_List.objects.filter(Company = com, name__iexact = name).exists():
                res = f'<script>alert("{name} already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)

            priceList = Fin_Price_List(
                Company = com, LoginDetails = data, name = name, type = type, item_rate = itemRate, description = description, currency = currency, up_or_down = upOrDown, percentage = percent, round_off = roundOff, status = 'Active'
            )
            priceList.save()

            #save transaction

            Fin_PriceList_Transaction_History.objects.create(
                Company = com,
                LoginDetails = data,
                list = priceList,
                action = 'Created'
            )

            if itemRate == 'Customized individual rate':
                itemName = request.POST.getlist('itemName[]')
                stdRate = request.POST.getlist('itemRateSale[]') if type == 'Sales' else request.POST.getlist('itemRatePurchase[]')
                customRate = request.POST.getlist('customRate[]')
                
                if len(itemName) == len(stdRate) == len(customRate):
                    values = zip(itemName,stdRate,customRate)
                    lis = list(values)

                    for ele in lis:
                        Fin_PriceList_Items.objects.get_or_create(Company = com, LoginDetails = data, list = priceList, item = Fin_Items.objects.get(id = int(ele[0])), standard_rate = float(ele[1]), custom_rate = float(ele[1]) if ele[2] == 0 or ele[2] =="0" else float(ele[2]))

                    return redirect(Fin_priceList)

                return redirect(Fin_addPriceList)

            return redirect(Fin_priceList)

        else:
                return redirect(Fin_addPriceList)
    else:
        return redirect('/')


def Fin_updatePriceList(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        lst = Fin_Price_List.objects.get(id = id)
        if request.method == 'POST':
            name = request.POST['name']
            type = request.POST['type']
            itemRate = request.POST['item_rate']
            description = request.POST['description']
            upOrDown = request.POST['up_or_down']
            percent = request.POST['percentage']
            roundOff = request.POST['round_off']
            currency = request.POST['currency']

            if lst.name != name and Fin_Price_List.objects.filter(Company = com, name__iexact = name).exists():
                res = f'<script>alert("{name} already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)

            if lst.item_rate == 'Customized individual rate' and itemRate != 'Customized individual rate':
                Fin_PriceList_Items.objects.filter(list = lst).delete()

            lst.name = name
            lst.type = type
            lst.item_rate = itemRate
            lst.description = description
            lst.currency = currency
            lst.up_or_down = upOrDown
            if itemRate == 'Customized individual rate':
                lst.percentage = None
                lst.round_off = None
            else:
                lst.percentage = percent
                lst.round_off = roundOff
            lst.save()

            #save transaction

            Fin_PriceList_Transaction_History.objects.create(
                Company = com,
                LoginDetails = data,
                list = lst,
                action = 'Edited'
            )

            itemName = request.POST.getlist('itemName[]')
            stdRate = request.POST.getlist('itemRateSale[]') if type == 'Sales' else request.POST.getlist('itemRatePurchase[]')
            customRate = request.POST.getlist('customRate[]')
            
            if itemRate == 'Customized individual rate':
                if Fin_PriceList_Items.objects.filter(list = lst).exists():
                    ids = request.POST.getlist('plItemId[]')
                    
                    if len(ids) == len(itemName) == len(stdRate) == len(customRate):
                        values = zip(ids, itemName,stdRate,customRate)
                        lis = list(values)

                        for ele in lis:
                            Fin_PriceList_Items.objects.filter(id = ele[0]).update(Company = com, LoginDetails = data, list = lst, item = Fin_Items.objects.get(id = int(ele[1])), standard_rate = float(ele[2]), custom_rate = float(ele[2]) if ele[3] == 0 or ele[3] =="0" else float(ele[3]))

                        return redirect(Fin_viewPriceList,id)

                    else:
                        return redirect(Fin_editPriceList, id)
                else:
                    if len(itemName) == len(stdRate) == len(customRate):
                        values = zip(itemName,stdRate,customRate)
                        lis = list(values)
                        for ele in lis:
                            Fin_PriceList_Items.objects.create(Company = com, LoginDetails = data, list = lst, item = Fin_Items.objects.get(id = int(ele[0])), standard_rate = float(ele[1]), custom_rate = float(ele[1]) if ele[2] == 0 or ele[2] =="0" else float(ele[2]))
                        
                        return redirect(Fin_viewPriceList,id)
            else:
                return redirect(Fin_viewPriceList,id)

        else:
            return redirect(Fin_editPriceList, id)
    else:
        return redirect('/')


def Fin_newCustomerPaymentTerm(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        term = request.POST['term']
        days = request.POST['days']

        if not Fin_Company_Payment_Terms.objects.filter(Company = com, term_name__iexact = term).exists():
            Fin_Company_Payment_Terms.objects.create(Company = com, term_name = term, days =days)
            
            list= []
            terms = Fin_Company_Payment_Terms.objects.filter(Company = com)

            for term in terms:
                termDict = {
                    'name': term.term_name,
                    'id': term.id,
                    'days':term.days
                }
                list.append(termDict)

            return JsonResponse({'status':True,'terms':list},safe=False)
        else:
            return JsonResponse({'status':False, 'message':f'{term} already exists, try another.!'})

    else:
        return redirect('/')


# -------------Shemeem--------Invoice & Vendors-------------------------------

# Invoice
        
def Fin_invoice(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            inv = Fin_Invoice.objects.filter(Company = com)
            return render(request,'company/Fin_Invoice.html',{'allmodules':allmodules,'com':com,'data':data,'invoices':inv})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            inv = Fin_Invoice.objects.filter(Company = com.company_id)
            return render(request,'company/Fin_Invoice.html',{'allmodules':allmodules,'com':com,'data':data,'invoices':inv})
    else:
       return redirect('/')
    
def Fin_addInvoice(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            cmp = com
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            cmp = com.company_id

        cust = Fin_Customers.objects.filter(Company = cmp, status = 'Active')
        itms = Fin_Items.objects.filter(Company = cmp, status = 'Active')
        trms = Fin_Company_Payment_Terms.objects.filter(Company = cmp)
        bnk = Fin_Banking.objects.filter(company = cmp)
        lst = Fin_Price_List.objects.filter(Company = cmp, status = 'Active')
        units = Fin_Units.objects.filter(Company = cmp)
        acc = Fin_Chart_Of_Account.objects.filter(Q(account_type='Expense') | Q(account_type='Other Expense') | Q(account_type='Cost Of Goods Sold'), Company=cmp).order_by('account_name')

        # Fetching last invoice and assigning upcoming ref no as current + 1
        # Also check for if any bill is deleted and ref no is continuos w r t the deleted invoice
        latest_inv = Fin_Invoice.objects.filter(Company = cmp).order_by('-id').first()

        new_number = int(latest_inv.reference_no) + 1 if latest_inv else 1

        if Fin_Invoice_Reference.objects.filter(Company = cmp).exists():
            deleted = Fin_Invoice_Reference.objects.get(Company = cmp)
            
            if deleted:
                while int(deleted.reference_no) >= new_number:
                    new_number+=1

        # Finding next invoice number w r t last invoic number if exists.
        nxtInv = ""
        lastInv = Fin_Invoice.objects.filter(Company = cmp).last()
        if lastInv:
            inv_no = str(lastInv.invoice_no)
            numbers = []
            stri = []
            for word in inv_no:
                if word.isdigit():
                    numbers.append(word)
                else:
                    stri.append(word)
            
            num=''
            for i in numbers:
                num +=i
            
            st = ''
            for j in stri:
                st = st+j

            inv_num = int(num)+1

            if num[0] == '0':
                if inv_num <10:
                    nxtInv = st+'0'+ str(inv_num)
                else:
                    nxtInv = st+ str(inv_num)
            else:
                nxtInv = st+ str(inv_num)

        context = {
            'allmodules':allmodules, 'com':com, 'cmp':cmp, 'data':data, 'customers':cust, 'items':itms, 'pTerms':trms,'list':lst,
            'ref_no':new_number,'banks':bnk,'invNo':nxtInv,'units':units, 'accounts':acc
        }
        return render(request,'company/Fin_Add_Invoice.html',context)
    else:
       return redirect('/')

def Fin_getBankAccount(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
        
        bankId = request.GET['id']
        bnk = Fin_Banking.objects.get(id = bankId)

        if bnk:
            return JsonResponse({'status':True, 'account':bnk.account_number})
        else:
            return JsonResponse({'status':False, 'message':'Something went wrong..!'})
    else:
       return redirect('/')
    
def Fin_getInvoiceCustomerData(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
        
        custId = request.POST['id']
        cust = Fin_Customers.objects.get(id = custId)

        if cust:
            if cust.price_list and cust.price_list.type == 'Sales':
                list = True
                listId = cust.price_list.id
                listName = cust.price_list.name
            else:
                list = False
                listId = None
                listName = None
            context = {
                'status':True, 'id':cust.id, 'email':cust.email, 'gstType':cust.gst_type,'shipState':cust.place_of_supply,'gstin':False if cust.gstin == "" or cust.gstin == None else True, 'gstNo':cust.gstin, 'priceList':list, 'ListId':listId, 'ListName':listName,
                'street':cust.billing_street, 'city':cust.billing_city, 'state':cust.billing_state, 'country':cust.billing_country, 'pincode':cust.billing_pincode
            }
            return JsonResponse(context)
        else:
            return JsonResponse({'status':False, 'message':'Something went wrong..!'})
    else:
       return redirect('/')

def Fin_checkInvoiceNumber(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        invNo = request.GET['invNum']

        nxtInv = ""
        lastInv = Fin_Invoice.objects.filter(Company = com).last()
        if lastInv:
            inv_no = str(lastInv.invoice_no)
            numbers = []
            stri = []
            for word in inv_no:
                if word.isdigit():
                    numbers.append(word)
                else:
                    stri.append(word)
            
            num=''
            for i in numbers:
                num +=i
            
            st = ''
            for j in stri:
                st = st+j

            inv_num = int(num)+1

            if num[0] == '0':
                if inv_num <10:
                    nxtInv = st+'0'+ str(inv_num)
                else:
                    nxtInv = st+ str(inv_num)
            else:
                nxtInv = st+ str(inv_num)

        if Fin_Invoice.objects.filter(Company = com, invoice_no__iexact = invNo).exists():
            return JsonResponse({'status':False, 'message':'Invoice No already Exists.!'})
        elif nxtInv != "" and invNo != nxtInv:
            return JsonResponse({'status':False, 'message':'Invoice No is not continuous.!'})
        else:
            return JsonResponse({'status':True, 'message':'Number is okay.!'})
    else:
       return redirect('/')
    
def Fin_getInvItemDetails(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        itemName = request.GET['item']
        print(itemName)
        # priceListId = request.GET['listId']
        item = Fin_Items.objects.get(Company = com, name = itemName)

        # if priceListId != "":
        #     priceList = Fin_Price_List.objects.get(id = int(priceListId))

        #     if priceList.item_rate == 'Customized individual rate':
        #         try:
        #             priceListPrice = float(Fin_PriceList_Items.objects.get(Company = com, list = priceList, item = item).custom_rate)
        #         except:
        #             priceListPrice = item.selling_price
        #     else:
        #         mark = priceList.up_or_down
        #         percentage = float(priceList.percentage)
        #         roundOff = priceList.round_off

        #         if mark == 'Markup':
        #             price = float(item.selling_price) + float((item.selling_price) * (percentage/100))
        #         else:
        #             price = float(item.selling_price) - float((item.selling_price) * (percentage/100))

        #         if priceList.round_off != 'Never mind':
        #             if roundOff == 'Nearest whole number':
        #                 finalPrice = round(price)
        #             else:
        #                 finalPrice = int(price) + float(roundOff)
        #         else:
        #             finalPrice = price

        #         priceListPrice = finalPrice
        # else:
        #     priceListPrice = None

        context = {
            'status':True,
            'id': item.id,
            'hsn':item.hsn,
            'sales_rate':item.selling_price,
            'purchase_rate':item.purchase_price,
            'avl':item.current_stock,
            'tax': True if item.tax_reference == 'taxable' else False,
            'gst':item.intra_state_tax,
            'igst':item.inter_state_tax,
            # 'PLPrice':priceListPrice,

        }
        return JsonResponse(context)
    else:
       return redirect('/')

def Fin_createInvoice(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        if request.method == 'POST':
            invNum = request.POST['invoice_no']
            if Fin_Invoice.objects.filter(Company = com, invoice_no__iexact = invNum).exists():
                res = f'<script>alert("Invoice Number `{invNum}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)

            inv = Fin_Invoice(
                Company = com,
                LoginDetails = com.Login_Id,
                Customer = Fin_Customers.objects.get(id = request.POST['customer']),
                customer_email = request.POST['customerEmail'],
                billing_address = request.POST['bill_address'],
                gst_type = request.POST['gst_type'],
                gstin = request.POST['gstin'],
                place_of_supply = request.POST['place_of_supply'],
                reference_no = request.POST['reference_number'],
                invoice_no = invNum,
                payment_terms = Fin_Company_Payment_Terms.objects.get(id = request.POST['payment_term']),
                invoice_date = request.POST['invoice_date'],
                duedate = datetime.strptime(request.POST['due_date'], '%d-%m-%Y').date(),
                salesOrder_no = request.POST['order_number'],
                exp_ship_date = None,
                price_list_applied = True if 'priceList' in request.POST else False,
                payment_method = None if request.POST['payment_method'] == "" else request.POST['payment_method'],
                cheque_no = None if request.POST['cheque_id'] == "" else request.POST['cheque_id'],
                upi_no = None if request.POST['upi_id'] == "" else request.POST['upi_id'],
                bank_acc_no = None if request.POST['bnk_id'] == "" else request.POST['bnk_id'],
                subtotal = 0.0 if request.POST['subtotal'] == "" else float(request.POST['subtotal']),
                igst = 0.0 if request.POST['igst'] == "" else float(request.POST['igst']),
                cgst = 0.0 if request.POST['cgst'] == "" else float(request.POST['cgst']),
                sgst = 0.0 if request.POST['sgst'] == "" else float(request.POST['sgst']),
                tax_amount = 0.0 if request.POST['taxamount'] == "" else float(request.POST['taxamount']),
                adjustment = 0.0 if request.POST['adj'] == "" else float(request.POST['adj']),
                shipping_charge = 0.0 if request.POST['ship'] == "" else float(request.POST['ship']),
                grandtotal = 0.0 if request.POST['grandtotal'] == "" else float(request.POST['grandtotal']),
                paid_off = 0.0 if request.POST['advance'] == "" else float(request.POST['advance']),
                balance = request.POST['grandtotal'] if request.POST['balance'] == "" else float(request.POST['balance']),
                note = request.POST['note']
            )

            inv.save()

            if len(request.FILES) != 0:
                inv.file=request.FILES.get('file')
            inv.save()

            if 'Draft' in request.POST:
                inv.status = "Draft"
            elif "Save" in request.POST:
                inv.status = "Saved" 
            inv.save()

            # Save invoice items.

            itemId = request.POST.getlist("item_id[]")
            itemName = request.POST.getlist("item_name[]")
            hsn  = request.POST.getlist("hsn[]")
            qty = request.POST.getlist("qty[]")
            price = request.POST.getlist("priceListPrice[]") if 'priceList' in request.POST else request.POST.getlist("price[]")
            tax = request.POST.getlist("taxGST[]") if request.POST['place_of_supply'] == com.State else request.POST.getlist("taxIGST[]")
            discount = request.POST.getlist("discount[]")
            total = request.POST.getlist("total[]")

            if len(itemId)==len(itemName)==len(hsn)==len(qty)==len(price)==len(tax)==len(discount)==len(total) and itemId and itemName and hsn and qty and price and tax and discount and total:
                mapped = zip(itemId,itemName,hsn,qty,price,tax,discount,total)
                mapped = list(mapped)
                for ele in mapped:
                    itm = Fin_Items.objects.get(id = int(ele[0]))
                    Fin_Invoice_Items.objects.create(Invoice = inv, Item = itm, hsn = ele[2], quantity = int(ele[3]), price = float(ele[4]), tax = ele[5], discount = float(ele[6]), total = float(ele[7]))
                    itm.current_stock -= int(ele[3])
                    itm.save()
            
            # Save transaction
                    
            Fin_Invoice_History.objects.create(
                Company = com,
                LoginDetails = data,
                Invoice = inv,
                action = 'Created'
            )

            return redirect(Fin_invoice)
        else:
            return redirect(Fin_addInvoice)
    else:
       return redirect('/')

def Fin_viewInvoice(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        inv = Fin_Invoice.objects.get(id = id)
        cmt = Fin_Invoice_Comments.objects.filter(Invoice = inv)
        hist = Fin_Invoice_History.objects.filter(Invoice = inv).last()
        invItems = Fin_Invoice_Items.objects.filter(Invoice = inv)
        created = Fin_Invoice_History.objects.get(Invoice = inv, action = 'Created')

        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            cmp = com
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            cmp = com.company_id
            allmodules = Fin_Modules_List.objects.get(company_id = cmp,status = 'New')
        
        return render(request,'company/Fin_View_Invoice.html',{'allmodules':allmodules,'com':com,'cmp':cmp, 'data':data, 'invoice':inv,'invItems':invItems, 'history':hist, 'comments':cmt, 'created':created})
    else:
       return redirect('/')

def Fin_convertInvoice(request,id):
    if 's_id' in request.session:

        inv = Fin_Invoice.objects.get(id = id)
        inv.status = 'Saved'
        inv.save()
        return redirect(Fin_viewInvoice, id)

def Fin_addInvoiceComment(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        inv = Fin_Invoice.objects.get(id = id)
        if request.method == "POST":
            cmt = request.POST['comment'].strip()

            Fin_Invoice_Comments.objects.create(Company = com, Invoice = inv, comments = cmt)
            return redirect(Fin_viewInvoice, id)
        return redirect(Fin_viewInvoice, id)
    return redirect('/')

def Fin_deleteInvoiceComment(request,id):
    if 's_id' in request.session:
        cmt = Fin_Invoice_Comments.objects.get(id = id)
        invId = cmt.Invoice.id
        cmt.delete()
        return redirect(Fin_viewInvoice, invId)
    
def Fin_invoiceHistory(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        inv = Fin_Invoice.objects.get(id = id)
        his = Fin_Invoice_History.objects.filter(Invoice = inv)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
        
        return render(request,'company/Fin_Invoice_History.html',{'allmodules':allmodules,'com':com,'data':data,'history':his, 'invoice':inv})
    else:
       return redirect('/')
    
def Fin_deleteInvoice(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        inv = Fin_Invoice.objects.get( id = id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        for i in Fin_Invoice_Items.objects.filter(Invoice = inv):
            item = Fin_Items.objects.get(id = i.Item.id)
            item.current_stock += i.quantity
            item.save()
        
        Fin_Invoice_Items.objects.filter(Invoice = inv).delete()

        # Storing ref number to deleted table
        # if entry exists and lesser than the current, update and save => Only one entry per company
        if Fin_Invoice_Reference.objects.filter(Company = com).exists():
            deleted = Fin_Invoice_Reference.objects.get(Company = com)
            if int(inv.reference_no) > int(deleted.reference_no):
                deleted.reference_no = inv.reference_no
                deleted.save()
        else:
            Fin_Invoice_Reference.objects.create(Company = com, reference_no = inv.reference_no)
        
        inv.delete()
        return redirect(Fin_invoice)
    
def Fin_invoicePdf(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        inv = Fin_Invoice.objects.get(id = id)
        itms = Fin_Invoice_Items.objects.filter(Invoice = inv)
    
        context = {'invoice':inv, 'invItems':itms,'cmp':com}
        
        template_path = 'company/Fin_Invoice_Pdf.html'
        fname = 'Invoice_'+inv.invoice_no
        # return render(request, 'company/Fin_Invoice_Pdf.html',context)
        # Create a Django response object, and specify content_type as pdftemp_
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] =f'attachment; filename = {fname}.pdf'
        # find the template and render it.
        template = get_template(template_path)
        html = template.render(context)

        # create a pdf
        pisa_status = pisa.CreatePDF(
        html, dest=response)
        # if error then show some funny view
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
    else:
        return redirect('/')

def Fin_shareInvoiceToEmail(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        inv = Fin_Invoice.objects.get(id = id)
        itms = Fin_Invoice_Items.objects.filter(Invoice = inv)
        try:
            if request.method == 'POST':
                emails_string = request.POST['email_ids']

                # Split the string by commas and remove any leading or trailing whitespace
                emails_list = [email.strip() for email in emails_string.split(',')]
                email_message = request.POST['email_message']
                # print(emails_list)
            
                context = {'invoice':inv, 'invItems':itms,'cmp':com}
                template_path = 'company/Fin_Invoice_Pdf.html'
                template = get_template(template_path)

                html  = template.render(context)
                result = BytesIO()
                pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
                pdf = result.getvalue()
                filename = f'Invoice_{inv.invoice_no}'
                subject = f"Invoice_{inv.invoice_no}"
                email = EmailMessage(subject, f"Hi,\nPlease find the attached Invoice for - INVOICE-{inv.invoice_no}. \n{email_message}\n\n--\nRegards,\n{com.Company_name}\n{com.Address}\n{com.State} - {com.Country}\n{com.Contact}", from_email=settings.EMAIL_HOST_USER, to=emails_list)
                email.attach(filename, pdf, "application/pdf")
                email.send(fail_silently=False)

                messages.success(request, 'Invoice details has been shared via email successfully..!')
                return redirect(Fin_viewInvoice,id)
        except Exception as e:
            print(e)
            messages.error(request, f'{e}')
            return redirect(Fin_viewInvoice, id)

def Fin_createInvoiceCustomer(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        fName = request.POST['first_name']
        lName = request.POST['last_name']
        gstIn = request.POST['gstin']
        pan = request.POST['pan_no']
        email = request.POST['email']
        phn = request.POST['mobile']

        if Fin_Customers.objects.filter(Company = com, first_name__iexact = fName, last_name__iexact = lName).exists():
            res = f"Customer `{fName} {lName}` already exists, try another!"
            return JsonResponse({'status': False, 'message':res})
        elif gstIn != "" and Fin_Customers.objects.filter(Company = com, gstin__iexact = gstIn).exists():
            res = f"GSTIN `{gstIn}` already exists, try another!"
            return JsonResponse({'status': False, 'message':res})
        elif Fin_Customers.objects.filter(Company = com, pan_no__iexact = pan).exists():
            res = f"PAN No `{pan}` already exists, try another!"
            return JsonResponse({'status': False, 'message':res})
        elif Fin_Customers.objects.filter(Company = com, mobile__iexact = phn).exists():
            res = f"Phone Number `{phn}` already exists, try another!"
            return JsonResponse({'status': False, 'message':res})
        elif Fin_Customers.objects.filter(Company = com, email__iexact = email).exists():
            res = f"Email `{email}` already exists, try another!"
            return JsonResponse({'status': False, 'message':res})

        cust = Fin_Customers(
            Company = com,
            LoginDetails = data,
            title = request.POST['title'],
            first_name = fName,
            last_name = lName,
            company = request.POST['company_name'],
            location = request.POST['location'],
            place_of_supply = request.POST['place_of_supply'],
            gst_type = request.POST['gst_type'],
            gstin = None if request.POST['gst_type'] == "Unregistered Business" or request.POST['gst_type'] == 'Overseas' or request.POST['gst_type'] == 'Consumer' else gstIn,
            pan_no = pan,
            email = email,
            mobile = phn,
            website = request.POST['website'],
            price_list = None if request.POST['price_list'] ==  "" else Fin_Price_List.objects.get(id = request.POST['price_list']),
            payment_terms = None if request.POST['payment_terms'] == "" else Fin_Company_Payment_Terms.objects.get(id = request.POST['payment_terms']),
            opening_balance = 0 if request.POST['open_balance'] == "" else float(request.POST['open_balance']),
            open_balance_type = request.POST['balance_type'],
            current_balance = 0 if request.POST['open_balance'] == "" else float(request.POST['open_balance']),
            credit_limit = 0 if request.POST['credit_limit'] == "" else float(request.POST['credit_limit']),
            billing_street = request.POST['street'],
            billing_city = request.POST['city'],
            billing_state = request.POST['state'],
            billing_pincode = request.POST['pincode'],
            billing_country = request.POST['country'],
            ship_street = request.POST['shipstreet'],
            ship_city = request.POST['shipcity'],
            ship_state = request.POST['shipstate'],
            ship_pincode = request.POST['shippincode'],
            ship_country = request.POST['shipcountry'],
            status = 'Active'
        )
        cust.save()

        #save transaction

        Fin_Customers_History.objects.create(
            Company = com,
            LoginDetails = data,
            customer = cust,
            action = 'Created'
        )

        return JsonResponse({'status': True})
    
    else:
        return redirect('/')
    
def Fin_getCustomers(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        options = {}
        option_objects = Fin_Customers.objects.filter(Company = com, status = 'Active')
        for option in option_objects:
            options[option.id] = [option.id , option.title, option.first_name, option.last_name]

        return JsonResponse(options)
    else:
        return redirect('/')
    
def Fin_createInvoiceItem(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        name = request.POST['name']
        type = request.POST['type']
        unit = request.POST.get('unit')
        hsn = request.POST['hsn']
        tax = request.POST['taxref']
        gstTax = 0 if tax == 'non taxable' else request.POST['intra_st']
        igstTax = 0 if tax == 'non taxable' else request.POST['inter_st']
        purPrice = request.POST['pcost']
        purAccount = None if not 'pur_account' in request.POST or request.POST['pur_account'] == "" else request.POST['pur_account']
        purDesc = request.POST['pur_desc']
        salePrice = request.POST['salesprice']
        saleAccount = None if not 'sale_account' in request.POST or request.POST['sale_account'] == "" else request.POST['sale_account']
        saleDesc = request.POST['sale_desc']
        inventory = request.POST.get('invacc')
        stock = 0 if request.POST.get('stock') == "" else request.POST.get('stock')
        stockUnitRate = 0 if request.POST.get('stock_rate') == "" else request.POST.get('stock_rate')
        minStock = request.POST['min_stock']
        createdDate = date.today()
        
        #save item and transaction if item or hsn doesn't exists already
        if Fin_Items.objects.filter(Company=com, name__iexact=name).exists():
            res = f"{name} already exists, try another!"
            return JsonResponse({'status': False, 'message':res})
        elif Fin_Items.objects.filter(Company = com, hsn__iexact = hsn).exists():
            res = f"HSN - {hsn} already exists, try another.!"
            return JsonResponse({'status': False, 'message':res})
        else:
            item = Fin_Items(
                Company = com,
                LoginDetails = data,
                name = name,
                item_type = type,
                unit = unit,
                hsn = hsn,
                tax_reference = tax,
                intra_state_tax = gstTax,
                inter_state_tax = igstTax,
                sales_account = saleAccount,
                selling_price = salePrice,
                sales_description = saleDesc,
                purchase_account = purAccount,
                purchase_price = purPrice,
                purchase_description = purDesc,
                item_created = createdDate,
                min_stock = minStock,
                inventory_account = inventory,
                opening_stock = stock,
                current_stock = stock,
                stock_in = 0,
                stock_out = 0,
                stock_unit_rate = stockUnitRate,
                status = 'Active'
            )
            item.save()

            #save transaction

            Fin_Items_Transaction_History.objects.create(
                Company = com,
                LoginDetails = data,
                item = item,
                action = 'Created'
            )
            
            return JsonResponse({'status': True})
    else:
       return redirect('/')

def Fin_getItems(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        items = {}
        option_objects = Fin_Items.objects.filter(Company = com, status='Active')
        for option in option_objects:
            items[option.name] = [option.name]

        return JsonResponse(items)
    else:
        return redirect('/')

def Fin_editInvoice(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            cmp = com
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            cmp = com.company_id

        inv = Fin_Invoice.objects.get(id = id)
        invItms = Fin_Invoice_Items.objects.filter(Invoice = inv)
        cust = Fin_Customers.objects.filter(Company = cmp, status = 'Active')
        itms = Fin_Items.objects.filter(Company = cmp, status = 'Active')
        trms = Fin_Company_Payment_Terms.objects.filter(Company = cmp)
        bnk = Fin_Banking.objects.filter(company = cmp)
        lst = Fin_Price_List.objects.filter(Company = cmp, status = 'Active')
        units = Fin_Units.objects.filter(Company = cmp)
        acc = Fin_Chart_Of_Account.objects.filter(Q(account_type='Expense') | Q(account_type='Other Expense') | Q(account_type='Cost Of Goods Sold'), Company=cmp).order_by('account_name')

        context = {
            'allmodules':allmodules, 'com':com, 'cmp':cmp, 'data':data,'invoice':inv, 'invItems':invItms, 'customers':cust, 'items':itms, 'pTerms':trms,'list':lst,
            'banks':bnk,'units':units, 'accounts':acc
        }
        return render(request,'company/Fin_Edit_Invoice.html',context)
    else:
       return redirect('/')

def Fin_updateInvoice(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        inv = Fin_Invoice.objects.get(id = id)
        if request.method == 'POST':
            invNum = request.POST['invoice_no']
            if inv.invoice_no != invNum and Fin_Invoice.objects.filter(Company = com, invoice_no__iexact = invNum).exists():
                res = f'<script>alert("Invoice Number `{invNum}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)

            inv.Customer = Fin_Customers.objects.get(id = request.POST['customer'])
            inv.customer_email = request.POST['customerEmail']
            inv.billing_address = request.POST['bill_address']
            inv.gst_type = request.POST['gst_type']
            inv.gstin = request.POST['gstin']
            inv.place_of_supply = request.POST['place_of_supply']
            inv.invoice_no = invNum
            inv.payment_terms = Fin_Company_Payment_Terms.objects.get(id = request.POST['payment_term'])
            inv.invoice_date = request.POST['invoice_date']
            inv.duedate = datetime.strptime(request.POST['due_date'], '%d-%m-%Y').date()
            inv.salesOrder_no = request.POST['order_number']
            inv.exp_ship_date = None
            inv.price_list_applied = True if 'priceList' in request.POST else False
            inv.payment_method = None if request.POST['payment_method'] == "" else request.POST['payment_method']
            inv.cheque_no = None if request.POST['cheque_id'] == "" else request.POST['cheque_id']
            inv.upi_no = None if request.POST['upi_id'] == "" else request.POST['upi_id']
            inv.bank_acc_no = None if request.POST['bnk_id'] == "" else request.POST['bnk_id']
            inv.subtotal = 0.0 if request.POST['subtotal'] == "" else float(request.POST['subtotal'])
            inv.igst = 0.0 if request.POST['igst'] == "" else float(request.POST['igst'])
            inv.cgst = 0.0 if request.POST['cgst'] == "" else float(request.POST['cgst'])
            inv.sgst = 0.0 if request.POST['sgst'] == "" else float(request.POST['sgst'])
            inv.tax_amount = 0.0 if request.POST['taxamount'] == "" else float(request.POST['taxamount'])
            inv.adjustment = 0.0 if request.POST['adj'] == "" else float(request.POST['adj'])
            inv.shipping_charge = 0.0 if request.POST['ship'] == "" else float(request.POST['ship'])
            inv.grandtotal = 0.0 if request.POST['grandtotal'] == "" else float(request.POST['grandtotal'])
            inv.paid_off = 0.0 if request.POST['advance'] == "" else float(request.POST['advance'])
            inv.balance = request.POST['grandtotal'] if request.POST['balance'] == "" else float(request.POST['balance'])
            inv.note = request.POST['note']

            if len(request.FILES) != 0:
                inv.file=request.FILES.get('file')

            inv.save()

            # Save invoice items.

            itemId = request.POST.getlist("item_id[]")
            itemName = request.POST.getlist("item_name[]")
            hsn  = request.POST.getlist("hsn[]")
            qty = request.POST.getlist("qty[]")
            price = request.POST.getlist("priceListPrice[]") if 'priceList' in request.POST else request.POST.getlist("price[]")
            tax = request.POST.getlist("taxGST[]") if request.POST['place_of_supply'] == com.State else request.POST.getlist("taxIGST[]")
            discount = request.POST.getlist("discount[]")
            total = request.POST.getlist("total[]")
            inv_item_ids = request.POST.getlist("id[]")
            invItem_ids = [int(id) for id in inv_item_ids]

            inv_items = Fin_Invoice_Items.objects.filter(Invoice = inv)
            object_ids = [obj.id for obj in inv_items]

            ids_to_delete = [obj_id for obj_id in object_ids if obj_id not in invItem_ids]
            for itmId in ids_to_delete:
                invItem = Fin_Invoice_Items.objects.get(id = itmId)
                item = Fin_Items.objects.get(id = invItem.Item.id)
                item.current_stock += invItem.quantity
                item.save()

            Fin_Invoice_Items.objects.filter(id__in=ids_to_delete).delete()
            
            count = Fin_Invoice_Items.objects.filter(Invoice = inv).count()

            if len(itemId)==len(itemName)==len(hsn)==len(qty)==len(price)==len(tax)==len(discount)==len(total)==len(invItem_ids) and invItem_ids and itemId and itemName and hsn and qty and price and tax and discount and total:
                mapped = zip(itemId,itemName,hsn,qty,price,tax,discount,total,invItem_ids)
                mapped = list(mapped)
                for ele in mapped:
                    if int(len(itemId))>int(count):
                        if ele[8] == 0:
                            itm = Fin_Items.objects.get(id = int(ele[0]))
                            Fin_Invoice_Items.objects.create(Invoice = inv, Item = itm, hsn = ele[2], quantity = int(ele[3]), price = float(ele[4]), tax = ele[5], discount = float(ele[6]), total = float(ele[7]))
                            itm.current_stock -= int(ele[3])
                            itm.save()
                        else:
                            itm = Fin_Items.objects.get(id = int(ele[0]))
                            inItm = Fin_Invoice_Items.objects.get(id = int(ele[8]))
                            crQty = int(inItm.quantity)
                            
                            Fin_Invoice_Items.objects.filter( id = int(ele[8])).update(Invoice = inv, Item = itm, hsn = ele[2], quantity = int(ele[3]), price = float(ele[4]), tax = ele[5], discount = float(ele[6]), total = float(ele[7]))
                            
                            if crQty < int(ele[3]):
                                itm.current_stock -=  abs(crQty - int(ele[3]))
                            elif crQty > int(ele[3]):
                                itm.current_stock += abs(crQty - int(ele[3]))
                            itm.save()
                    else:
                        itm = Fin_Items.objects.get(id = int(ele[0]))
                        inItm = Fin_Invoice_Items.objects.get(id = int(ele[8]))
                        crQty = int(inItm.quantity)

                        Fin_Invoice_Items.objects.filter( id = int(ele[8])).update(Invoice = inv, Item = itm, hsn = ele[2], quantity = int(ele[3]), price = float(ele[4]), tax = ele[5], discount = float(ele[6]), total = float(ele[7]))

                        if crQty < int(ele[3]):
                            itm.current_stock -=  abs(crQty - int(ele[3]))
                        elif crQty > int(ele[3]):
                            itm.current_stock += abs(crQty - int(ele[3]))
                        itm.save()
            
            # Save transaction
                    
            Fin_Invoice_History.objects.create(
                Company = com,
                LoginDetails = data,
                Invoice = inv,
                action = 'Edited'
            )

            return redirect(Fin_viewInvoice, id)
        else:
            return redirect(Fin_editInvoice, id)
    else:
       return redirect('/')
# Vendors
        
def Fin_vendors(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            vnd = Fin_Vendors.objects.filter(Company = com)
            return render(request,'company/Fin_Vendors.html',{'allmodules':allmodules,'com':com,'data':data,'vendors':vnd})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            vnd = Fin_Vendors.objects.filter(Company = com.company_id)
            return render(request,'company/Fin_Vendors.html',{'allmodules':allmodules,'com':com,'data':data,'vendors':vnd})
    else:
       return redirect('/')

def Fin_addVendor(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            trms = Fin_Company_Payment_Terms.objects.filter(Company = com)
            lst = Fin_Price_List.objects.filter(Company = com, status = 'Active')
            return render(request,'company/Fin_Add_Vendor.html',{'allmodules':allmodules,'com':com,'data':data, 'pTerms':trms, 'list':lst})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            trms = Fin_Company_Payment_Terms.objects.filter(Company = com.company_id)
            lst = Fin_Price_List.objects.filter(Company = com.company_id, status = 'Active')
            return render(request,'company/Fin_Add_Vendor.html',{'allmodules':allmodules,'com':com,'data':data, 'pTerms':trms, 'list':lst})
    else:
       return redirect('/')

def Fin_checkVendorName(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        fName = request.POST['fname']
        lName = request.POST['lname']

        if Fin_Vendors.objects.filter(Company = com, first_name__iexact = fName, last_name__iexact = lName).exists():
            msg = f'{fName} {lName} already exists, Try another.!'
            return JsonResponse({'is_exist':True, 'message':msg})
        else:
            return JsonResponse({'is_exist':False})
    else:
        return redirect('/')
    
def Fin_checkVendorGSTIN(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        gstIn = request.POST['gstin']

        if Fin_Vendors.objects.filter(Company = com, gstin__iexact = gstIn).exists():
            msg = f'{gstIn} already exists, Try another.!'
            return JsonResponse({'is_exist':True, 'message':msg})
        else:
            return JsonResponse({'is_exist':False})
    else:
        return redirect('/')
    
def Fin_checkVendorPAN(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        pan = request.POST['pan']

        if Fin_Vendors.objects.filter(Company = com, pan_no__iexact = pan).exists():
            msg = f'{pan} already exists, Try another.!'
            return JsonResponse({'is_exist':True, 'message':msg})
        else:
            return JsonResponse({'is_exist':False})
    else:
        return redirect('/')

def Fin_checkVendorPhone(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        phn = request.POST['phone']

        if Fin_Vendors.objects.filter(Company = com, mobile__iexact = phn).exists():
            msg = f'{phn} already exists, Try another.!'
            return JsonResponse({'is_exist':True, 'message':msg})
        else:
            return JsonResponse({'is_exist':False})
    else:
        return redirect('/')

def Fin_checkVendorEmail(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        email = request.POST['email']

        if Fin_Vendors.objects.filter(Company = com, email__iexact = email).exists():
            msg = f'{email} already exists, Try another.!'
            return JsonResponse({'is_exist':True, 'message':msg})
        else:
            return JsonResponse({'is_exist':False})
    else:
        return redirect('/')

def Fin_createVendor(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        if request.method == 'POST':
            fName = request.POST['first_name']
            lName = request.POST['last_name']
            gstIn = request.POST['gstin']
            pan = request.POST['pan_no']
            email = request.POST['email']
            phn = request.POST['mobile']

            if Fin_Vendors.objects.filter(Company = com, first_name__iexact = fName, last_name__iexact = lName).exists():
                res = f'<script>alert("Vendor `{fName} {lName}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)
            elif Fin_Vendors.objects.filter(Company = com, gstin__iexact = gstIn).exists():
                res = f'<script>alert("GSTIN `{gstIn}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)
            elif Fin_Vendors.objects.filter(Company = com, pan_no__iexact = pan).exists():
                res = f'<script>alert("PAN No `{pan}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)
            elif Fin_Vendors.objects.filter(Company = com, mobile__iexact = phn).exists():
                res = f'<script>alert("Phone Number `{phn}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)
            elif Fin_Vendors.objects.filter(Company = com, email__iexact = email).exists():
                res = f'<script>alert("Email `{email}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)

            vnd = Fin_Vendors(
                Company = com,
                LoginDetails = com.Login_Id,
                title = request.POST['title'],
                first_name = fName,
                last_name = lName,
                company = request.POST['company_name'],
                location = request.POST['location'],
                place_of_supply = request.POST['place_of_supply'],
                gst_type = request.POST['gst_type'],
                gstin = None if request.POST['gst_type'] == "Unregistered Business" or request.POST['gst_type'] == 'Overseas' or request.POST['gst_type'] == 'Consumer' else gstIn,
                pan_no = pan,
                email = email,
                mobile = phn,
                website = request.POST['website'],
                price_list = None if request.POST['price_list'] ==  "" else Fin_Price_List.objects.get(id = request.POST['price_list']),
                payment_terms = None if request.POST['payment_terms'] == "" else Fin_Company_Payment_Terms.objects.get(id = request.POST['payment_terms']),
                opening_balance = 0 if request.POST['open_balance'] == "" else float(request.POST['open_balance']),
                open_balance_type = request.POST['balance_type'],
                current_balance = 0 if request.POST['open_balance'] == "" else float(request.POST['open_balance']),
                credit_limit = 0 if request.POST['credit_limit'] == "" else float(request.POST['credit_limit']) * -1,
                currency = request.POST['currency'],
                billing_street = request.POST['street'],
                billing_city = request.POST['city'],
                billing_state = request.POST['state'],
                billing_pincode = request.POST['pincode'],
                billing_country = request.POST['country'],
                ship_street = request.POST['shipstreet'],
                ship_city = request.POST['shipcity'],
                ship_state = request.POST['shipstate'],
                ship_pincode = request.POST['shippincode'],
                ship_country = request.POST['shipcountry'],
                status = 'Active'
            )
            vnd.save()

            #save transaction

            Fin_Vendor_History.objects.create(
                Company = com,
                LoginDetails = data,
                Vendor = vnd,
                action = 'Created'
            )

            return redirect(Fin_vendors)

        else:
            return redirect(Fin_addVendor)
    else:
        return redirect('/')

def Fin_viewVendor(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            cmp = com
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            cmp = com.company_id
        
        vnd = Fin_Vendors.objects.get(id = id)
        cmt = Fin_Vendor_Comments.objects.filter(Vendor = vnd)
        hist = Fin_Vendor_History.objects.filter(Vendor = vnd).last()

        # Collect data from sales,purchase and other req tables and add or substract balnace amount with 'Bal' based on its type.
        # Create dict with data -> Type, Number, Date, Total, Balance and append it with 'combined_data' list.
        # Pass 'combined_data' list and Final 'Bal' as BALANCE with context dict after fetching all req data.

        Bal = 0
        combined_data=[]
        
        # Vendor opening balance.
        dict = {
            'Type' : 'Opening Balance', 'Number' : "", 'Date' : vnd.date, 'Total': vnd.opening_balance, 'Balance': vnd.opening_balance
        }
        combined_data.append(dict)

        if vnd.open_balance_type == 'credit':
            Bal += float(vnd.opening_balance)
        else:
            Bal -= float(vnd.opening_balance)

        # Vendor Purchase order, Purchase bill, expense, recurring bill etc, goes here..

        context = {'allmodules':allmodules,'com':com,'cmp':cmp,'data':data, 'vendor':vnd, 'history':hist, 'comments':cmt, 'BALANCE':Bal, 'combined_data':combined_data}

        return render(request,'company/Fin_View_Vendor.html', context)

    else:
       return redirect('/')

def Fin_changeVendorStatus(request,id,status):
    if 's_id' in request.session:
        
        vnd = Fin_Vendors.objects.get(id = id)
        vnd.status = status
        vnd.save()
        return redirect(Fin_viewVendor, id)

def Fin_deleteVendor(request, id):
    if 's_id' in request.session:
        vnd = Fin_Vendors.objects.get( id = id)
        vnd.delete()
        return redirect(Fin_vendors)

def Fin_vendorHistory(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        vnd = Fin_Vendors.objects.get(id = id)
        his = Fin_Vendor_History.objects.filter(Vendor = vnd)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            return render(request,'company/Fin_Vendor_History.html',{'allmodules':allmodules,'com':com,'data':data,'history':his, 'vendor':vnd})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            return render(request,'company/Fin_Vendor_History.html',{'allmodules':allmodules,'com':com,'data':data,'history':his, 'vendor':vnd})
    else:
       return redirect('/')

def Fin_editVendor(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        vnd = Fin_Vendors.objects.get(id = id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            trms = Fin_Company_Payment_Terms.objects.filter(Company = com)
            lst = Fin_Price_List.objects.filter(Company = com, status = 'Active')
            return render(request,'company/Fin_Edit_Vendor.html',{'allmodules':allmodules,'com':com,'data':data, 'vendor':vnd, 'pTerms':trms, 'list':lst})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            trms = Fin_Company_Payment_Terms.objects.filter(Company = com.company_id)
            lst = Fin_Price_List.objects.filter(Company = com.company_id, status = 'Active')
            return render(request,'company/Fin_Edit_Vendor.html',{'allmodules':allmodules,'com':com,'data':data, 'vendor':vnd, 'pTerms':trms, 'list':lst})
    else:
       return redirect('/')

def Fin_updateVendor(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        vnd = Fin_Vendors.objects.get(id = id)
        if request.method == 'POST':
            fName = request.POST['first_name']
            lName = request.POST['last_name']
            gstIn = request.POST['gstin']
            pan = request.POST['pan_no']
            email = request.POST['email']
            phn = request.POST['mobile']

            if vnd.first_name != fName and vnd.last_name != lName and Fin_Vendors.objects.filter(Company = com, first_name__iexact = fName, last_name__iexact = lName).exists():
                res = f'<script>alert("Vendor `{fName} {lName}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)
            elif vnd.gstin != gstIn and Fin_Vendors.objects.filter(Company = com, gstin__iexact = gstIn).exists():
                res = f'<script>alert("GSTIN `{gstIn}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)
            elif vnd.pan_no != pan and Fin_Vendors.objects.filter(Company = com, pan_no__iexact = pan).exists():
                res = f'<script>alert("PAN No `{pan}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)
            elif vnd.mobile != phn and Fin_Vendors.objects.filter(Company = com, mobile__iexact = phn).exists():
                res = f'<script>alert("Phone Number `{phn}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)
            elif vnd.email != email and Fin_Vendors.objects.filter(Company = com, email__iexact = email).exists():
                res = f'<script>alert("Email `{email}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)

            vnd.title = request.POST['title']
            vnd.first_name = fName
            vnd.last_name = lName
            vnd.company = request.POST['company_name']
            vnd.location = request.POST['location']
            vnd.place_of_supply = request.POST['place_of_supply']
            vnd.gst_type = request.POST['gst_type']
            vnd.gstin = None if request.POST['gst_type'] == "Unregistered Business" or request.POST['gst_type'] == 'Overseas' or request.POST['gst_type'] == 'Consumer' else gstIn
            vnd.pan_no = pan
            vnd.email = email
            vnd.mobile = phn
            vnd.website = request.POST['website']
            vnd.price_list = None if request.POST['price_list'] ==  "" else Fin_Price_List.objects.get(id = request.POST['price_list'])
            vnd.payment_terms = None if request.POST['payment_terms'] == "" else Fin_Company_Payment_Terms.objects.get(id = request.POST['payment_terms'])
            vnd.opening_balance = 0 if request.POST['open_balance'] == "" else float(request.POST['open_balance'])
            vnd.open_balance_type = request.POST['balance_type']
            vnd.current_balance = 0 if request.POST['open_balance'] == "" else float(request.POST['open_balance'])
            vnd.credit_limit = 0 if request.POST['credit_limit'] == "" else float(request.POST['credit_limit']) * -1
            vnd.currency = request.POST['currency']
            vnd.billing_street = request.POST['street']
            vnd.billing_city = request.POST['city']
            vnd.billing_state = request.POST['state']
            vnd.billing_pincode = request.POST['pincode']
            vnd.billing_country = request.POST['country']
            vnd.ship_street = request.POST['shipstreet']
            vnd.ship_city = request.POST['shipcity']
            vnd.ship_state = request.POST['shipstate']
            vnd.ship_pincode = request.POST['shippincode']
            vnd.ship_country = request.POST['shipcountry']

            vnd.save()

            #save transaction

            Fin_Vendor_History.objects.create(
                Company = com,
                LoginDetails = data,
                Vendor = vnd,
                action = 'Edited'
            )

            return redirect(Fin_viewVendor, id)

        else:
            return redirect(Fin_editVendor, id)
    else:
        return redirect('/')

def Fin_addVendorComment(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        vnd = Fin_Vendors.objects.get(id = id)
        if request.method == "POST":
            cmt = request.POST['comment'].strip()

            Fin_Vendor_Comments.objects.create(Company = com, Vendor = vnd, comments = cmt)
            return redirect(Fin_viewVendor, id)
        return redirect(Fin_viewVendor, id)
    return redirect('/')

def Fin_deleteVendorComment(request,id):
    if 's_id' in request.session:
        cmt = Fin_Vendor_Comments.objects.get(id = id)
        vendorId = cmt.Vendor.id
        cmt.delete()
        return redirect(Fin_viewVendor, vendorId)

def Fin_vendorTransactionsPdf(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        vnd = Fin_Vendors.objects.get(id = id)

        Bal = 0
        combined_data=[]
        
        # Vendor opening balance.
        dict = {
            'Type' : 'Opening Balance', 'Number' : "", 'Date' : vnd.date, 'Total': vnd.opening_balance, 'Balance': vnd.opening_balance
        }
        combined_data.append(dict)

        if vnd.open_balance_type == 'credit':
            Bal += float(vnd.opening_balance)
        else:
            Bal -= float(vnd.opening_balance)
    
        context = {'vendor':vnd, 'cmp':com, 'BALANCE':Bal, 'combined_data':combined_data}
        
        template_path = 'company/Fin_Vendor_Transaction_Pdf.html'
        fname = 'Vendor_Transactions_'+vnd.first_name+'_'+vnd.last_name
        # return render(request, 'company/Fin_Vendor_Transaction_Pdf.html',context)
        # Create a Django response object, and specify content_type as pdftemp_
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] =f'attachment; filename = {fname}.pdf'
        # find the template and render it.
        template = get_template(template_path)
        html = template.render(context)

        # create a pdf
        pisa_status = pisa.CreatePDF(
        html, dest=response)
        # if error then show some funny view
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
    else:
        return redirect('/')
    
def Fin_shareVendorTransactionsToEmail(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        try:
            if request.method == 'POST':
                emails_string = request.POST['email_ids']

                # Split the string by commas and remove any leading or trailing whitespace
                emails_list = [email.strip() for email in emails_string.split(',')]
                email_message = request.POST['email_message']
                # print(emails_list)
            
                vnd = Fin_Vendors.objects.get(id = id)

                Bal = 0
                combined_data=[]
                
                # Vendor opening balance.
                dict = {
                    'Type' : 'Opening Balance', 'Number' : "", 'Date' : vnd.date, 'Total': vnd.opening_balance, 'Balance': vnd.opening_balance
                }
                combined_data.append(dict)

                if vnd.open_balance_type == 'credit':
                    Bal += float(vnd.opening_balance)
                else:
                    Bal -= float(vnd.opening_balance)
            
                context = {'vendor':vnd, 'cmp':com, 'BALANCE':Bal, 'combined_data':combined_data}
                template_path = 'company/Fin_Vendor_Transaction_Pdf.html'
                template = get_template(template_path)

                html  = template.render(context)
                result = BytesIO()
                pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
                pdf = result.getvalue()
                filename = f'Vendor_Transactions_{vnd.first_name}_{vnd.last_name}'
                subject = f"Vendor_Transactions_{vnd.first_name}_{vnd.last_name}"
                email = EmailMessage(subject, f"Hi,\nPlease find the attached Transaction details for - Vendor-{vnd.first_name} {vnd.last_name}. \n{email_message}\n\n--\nRegards,\n{com.Company_name}\n{com.Address}\n{com.State} - {com.Country}\n{com.Contact}", from_email=settings.EMAIL_HOST_USER, to=emails_list)
                email.attach(filename, pdf, "application/pdf")
                email.send(fail_silently=False)

                messages.success(request, 'Transactions details has been shared via email successfully..!')
                return redirect(Fin_viewVendor,id)
        except Exception as e:
            print(e)
            messages.error(request, f'{e}')
            return redirect(Fin_viewVendor, id)

#End

# -------------Shemeem--------Sales Order-------------------------------
        
def Fin_salesOrder(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            cmp = com
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            cmp = com.company_id
        
        salesOrders = Fin_Sales_Order.objects.filter(Company = cmp)
        return render(request,'company/Fin_Sales_Order.html',{'allmodules':allmodules,'com':com, 'cmp':cmp,'data':data,'sales_orders':salesOrders})
    else:
       return redirect('/')

def Fin_addSalesOrder(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            cmp = com
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            cmp = com.company_id

        cust = Fin_Customers.objects.filter(Company = cmp, status = 'Active')
        itms = Fin_Items.objects.filter(Company = cmp, status = 'Active')
        trms = Fin_Company_Payment_Terms.objects.filter(Company = cmp)
        bnk = Fin_Banking.objects.filter(company = cmp)
        lst = Fin_Price_List.objects.filter(Company = cmp, status = 'Active')
        units = Fin_Units.objects.filter(Company = cmp)
        acc = Fin_Chart_Of_Account.objects.filter(Q(account_type='Expense') | Q(account_type='Other Expense') | Q(account_type='Cost Of Goods Sold'), Company=cmp).order_by('account_name')

        # Fetching last sales order and assigning upcoming ref no as current + 1
        # Also check for if any bill is deleted and ref no is continuos w r t the deleted sales order
        latest_so = Fin_Sales_Order.objects.filter(Company = cmp).order_by('-id').first()

        new_number = int(latest_so.reference_no) + 1 if latest_so else 1

        if Fin_Sales_Order_Reference.objects.filter(Company = cmp).exists():
            deleted = Fin_Sales_Order_Reference.objects.get(Company = cmp)
            
            if deleted:
                while int(deleted.reference_no) >= new_number:
                    new_number+=1

        # Finding next SO number w r t last SO number if exists.
        nxtSO = ""
        lastSO = Fin_Sales_Order.objects.filter(Company = cmp).last()
        if lastSO:
            salesOrder_no = str(lastSO.sales_order_no)
            numbers = []
            stri = []
            for word in salesOrder_no:
                if word.isdigit():
                    numbers.append(word)
                else:
                    stri.append(word)
            
            num=''
            for i in numbers:
                num +=i
            
            st = ''
            for j in stri:
                st = st+j

            s_order_num = int(num)+1

            if num[0] == '0':
                if s_order_num <10:
                    nxtSO = st+'0'+ str(s_order_num)
                else:
                    nxtSO = st+ str(s_order_num)
            else:
                nxtSO = st+ str(s_order_num)

        context = {
            'allmodules':allmodules, 'com':com, 'cmp':cmp, 'data':data, 'customers':cust, 'items':itms, 'pTerms':trms,'list':lst,
            'ref_no':new_number,'banks':bnk,'SONo':nxtSO,'units':units, 'accounts':acc
        }
        return render(request,'company/Fin_Add_Sales_Order.html',context)
    else:
       return redirect('/')

def Fin_createSalesOrder(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        if request.method == 'POST':
            SONum = request.POST['sales_order_no']
            if Fin_Sales_Order.objects.filter(Company = com, sales_order_no__iexact = SONum).exists():
                res = f'<script>alert("Sales Order Number `{SONum}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)

            SOrder = Fin_Sales_Order(
                Company = com,
                LoginDetails = com.Login_Id,
                Customer = None if request.POST['customerId'] == "" else Fin_Customers.objects.get(id = request.POST['customerId']),
                customer_email = request.POST['customerEmail'],
                billing_address = request.POST['bill_address'],
                gst_type = request.POST['gst_type'],
                gstin = request.POST['gstin'],
                place_of_supply = request.POST['place_of_supply'],
                reference_no = request.POST['reference_number'],
                sales_order_no = SONum,
                payment_terms = Fin_Company_Payment_Terms.objects.get(id = request.POST['payment_term']),
                sales_order_date = request.POST['sales_order_date'],
                exp_ship_date = datetime.strptime(request.POST['shipment_date'], '%d-%m-%Y').date(),
                payment_method = None if request.POST['payment_method'] == "" else request.POST['payment_method'],
                cheque_no = None if request.POST['cheque_id'] == "" else request.POST['cheque_id'],
                upi_no = None if request.POST['upi_id'] == "" else request.POST['upi_id'],
                bank_acc_no = None if request.POST['bnk_id'] == "" else request.POST['bnk_id'],
                subtotal = 0.0 if request.POST['subtotal'] == "" else float(request.POST['subtotal']),
                igst = 0.0 if request.POST['igst'] == "" else float(request.POST['igst']),
                cgst = 0.0 if request.POST['cgst'] == "" else float(request.POST['cgst']),
                sgst = 0.0 if request.POST['sgst'] == "" else float(request.POST['sgst']),
                tax_amount = 0.0 if request.POST['taxamount'] == "" else float(request.POST['taxamount']),
                adjustment = 0.0 if request.POST['adj'] == "" else float(request.POST['adj']),
                shipping_charge = 0.0 if request.POST['ship'] == "" else float(request.POST['ship']),
                grandtotal = 0.0 if request.POST['grandtotal'] == "" else float(request.POST['grandtotal']),
                paid_off = 0.0 if request.POST['advance'] == "" else float(request.POST['advance']),
                balance = request.POST['grandtotal'] if request.POST['balance'] == "" else float(request.POST['balance']),
                note = request.POST['note']
            )

            SOrder.save()

            if len(request.FILES) != 0:
                SOrder.file=request.FILES.get('file')
            SOrder.save()

            if 'Draft' in request.POST:
                SOrder.status = "Draft"
            elif "Save" in request.POST:
                SOrder.status = "Saved" 
            SOrder.save()

            # Save Sales Order items.

            itemId = request.POST.getlist("item_id[]")
            itemName = request.POST.getlist("item_name[]")
            hsn  = request.POST.getlist("hsn[]")
            qty = request.POST.getlist("qty[]")
            price = request.POST.getlist("price[]")
            tax = request.POST.getlist("taxGST[]") if request.POST['place_of_supply'] == com.State else request.POST.getlist("taxIGST[]")
            discount = request.POST.getlist("discount[]")
            total = request.POST.getlist("total[]")

            if len(itemId)==len(itemName)==len(hsn)==len(qty)==len(price)==len(tax)==len(discount)==len(total) and itemId and itemName and hsn and qty and price and tax and discount and total:
                mapped = zip(itemId,itemName,hsn,qty,price,tax,discount,total)
                mapped = list(mapped)
                for ele in mapped:
                    itm = Fin_Items.objects.get(id = int(ele[0]))
                    Fin_Sales_Order_Items.objects.create(SalesOrder = SOrder, Item = itm, hsn = ele[2], quantity = int(ele[3]), price = float(ele[4]), tax = ele[5], discount = float(ele[6]), total = float(ele[7]))
                    # itm.current_stock -= int(ele[3])
                    # itm.save()
            
            # Save transaction
                    
            Fin_Sales_Order_History.objects.create(
                Company = com,
                LoginDetails = data,
                SalesOrder = SOrder,
                action = 'Created'
            )

            return redirect(Fin_salesOrder)
        else:
            return redirect(Fin_addSalesOrder)
    else:
       return redirect('/')

def Fin_checkSalesOrderNumber(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        SONo = request.GET['SONum']

        nxtSO = ""
        lastSOrder = Fin_Sales_Order.objects.filter(Company = com).last()
        if lastSOrder:
            salesOrder_no = str(lastSOrder.sales_order_no)
            numbers = []
            stri = []
            for word in salesOrder_no:
                if word.isdigit():
                    numbers.append(word)
                else:
                    stri.append(word)
            
            num=''
            for i in numbers:
                num +=i
            
            st = ''
            for j in stri:
                st = st+j

            s_order_num = int(num)+1

            if num[0] == '0':
                if s_order_num <10:
                    nxtSO = st+'0'+ str(s_order_num)
                else:
                    nxtSO = st+ str(s_order_num)
            else:
                nxtSO = st+ str(s_order_num)

        if Fin_Sales_Order.objects.filter(Company = com, sales_order_no__iexact = SONo).exists():
            return JsonResponse({'status':False, 'message':'Sales Order No. already Exists.!'})
        elif nxtSO != "" and SONo != nxtSO:
            return JsonResponse({'status':False, 'message':'Sales Order No. is not continuous.!'})
        else:
            return JsonResponse({'status':True, 'message':'Number is okay.!'})
    else:
       return redirect('/')

def Fin_viewSalesOrder(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        salesOrder = Fin_Sales_Order.objects.get(id = id)
        cmt = Fin_Sales_Order_Comments.objects.filter(SalesOrder = salesOrder)
        hist = Fin_Sales_Order_History.objects.filter(SalesOrder = salesOrder).last()
        SOItems = Fin_Sales_Order_Items.objects.filter(SalesOrder = salesOrder)
        try:
            created = Fin_Sales_Order_History.objects.get(SalesOrder = salesOrder, action = 'Created')
        except:
            created = None

        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            cmp = com
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            cmp = com.company_id
            allmodules = Fin_Modules_List.objects.get(company_id = cmp,status = 'New')
        
        return render(request,'company/Fin_View_Sales_Order.html',{'allmodules':allmodules,'com':com,'cmp':cmp, 'data':data, 'order':salesOrder,'orderItems':SOItems, 'history':hist, 'comments':cmt, 'created':created})
    else:
       return redirect('/')

def Fin_convertSalesOrder(request,id):
    if 's_id' in request.session:

        salesOrder = Fin_Sales_Order.objects.get(id = id)
        salesOrder.status = 'Saved'
        salesOrder.save()
        return redirect(Fin_viewSalesOrder, id)

def Fin_addSalesOrderComment(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        salesOrder = Fin_Sales_Order.objects.get(id = id)
        if request.method == "POST":
            cmt = request.POST['comment'].strip()

            Fin_Sales_Order_Comments.objects.create(Company = com, SalesOrder = salesOrder, comments = cmt)
            return redirect(Fin_viewSalesOrder, id)
        return redirect(Fin_viewSalesOrder, id)
    return redirect('/')

def Fin_deleteSalesOrderComment(request,id):
    if 's_id' in request.session:
        cmt = Fin_Sales_Order_Comments.objects.get(id = id)
        orderId = cmt.SalesOrder.id
        cmt.delete()
        return redirect(Fin_viewSalesOrder, orderId)
    
def Fin_salesOrderHistory(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        salesOrder = Fin_Sales_Order.objects.get(id = id)
        his = Fin_Sales_Order_History.objects.filter(SalesOrder = salesOrder)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
        
        return render(request,'company/Fin_Sales_Order_History.html',{'allmodules':allmodules,'com':com,'data':data,'history':his, 'order':salesOrder})
    else:
       return redirect('/')
    
def Fin_deleteSalesOrder(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        salesOrder = Fin_Sales_Order.objects.get( id = id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        Fin_Sales_Order_Items.objects.filter(SalesOrder = salesOrder).delete()

        # Storing ref number to deleted table
        # if entry exists and lesser than the current, update and save => Only one entry per company
        if Fin_Sales_Order_Reference.objects.filter(Company = com).exists():
            deleted = Fin_Sales_Order_Reference.objects.get(Company = com)
            if int(salesOrder.reference_no) > int(deleted.reference_no):
                deleted.reference_no = salesOrder.reference_no
                deleted.save()
        else:
            Fin_Sales_Order_Reference.objects.create(Company = com, reference_no = salesOrder.reference_no)
        
        salesOrder.delete()
        return redirect(Fin_salesOrder)

def Fin_editSalesOrder(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            cmp = com
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            cmp = com.company_id

        salesOrder = Fin_Sales_Order.objects.get(id = id)
        SOItms = Fin_Sales_Order_Items.objects.filter(SalesOrder = salesOrder)
        cust = Fin_Customers.objects.filter(Company = cmp, status = 'Active')
        itms = Fin_Items.objects.filter(Company = cmp, status = 'Active')
        trms = Fin_Company_Payment_Terms.objects.filter(Company = cmp)
        bnk = Fin_Banking.objects.filter(company = cmp)
        lst = Fin_Price_List.objects.filter(Company = cmp, status = 'Active')
        units = Fin_Units.objects.filter(Company = cmp)
        acc = Fin_Chart_Of_Account.objects.filter(Q(account_type='Expense') | Q(account_type='Other Expense') | Q(account_type='Cost Of Goods Sold'), Company=cmp).order_by('account_name')

        context = {
            'allmodules':allmodules, 'com':com, 'cmp':cmp, 'data':data,'order':salesOrder, 'orderItems':SOItms, 'customers':cust, 'items':itms, 'pTerms':trms,'list':lst,
            'banks':bnk,'units':units, 'accounts':acc
        }
        return render(request,'company/Fin_Edit_Sales_Order.html',context)
    else:
       return redirect('/')

def Fin_updateSalesOrder(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        salesOrder = Fin_Sales_Order.objects.get(id = id)
        if request.method == 'POST':
            SONum = request.POST['sales_order_no']
            if salesOrder.sales_order_no != SONum and Fin_Sales_Order.objects.filter(Company = com, sales_order_no__iexact = SONum).exists():
                res = f'<script>alert("Sales Order Number `{SONum}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)

            salesOrder.Customer = None if request.POST['customerId'] == "" else Fin_Customers.objects.get(id = request.POST['customerId'])
            salesOrder.customer_email = request.POST['customerEmail']
            salesOrder.billing_address = request.POST['bill_address']
            salesOrder.gst_type = request.POST['gst_type']
            salesOrder.gstin = request.POST['gstin']
            salesOrder.place_of_supply = request.POST['place_of_supply']

            salesOrder.sales_order_no = SONum
            salesOrder.payment_terms = Fin_Company_Payment_Terms.objects.get(id = request.POST['payment_term'])
            salesOrder.sales_order_date = request.POST['sales_order_date']
            salesOrder.exp_ship_date = datetime.strptime(request.POST['shipment_date'], '%d-%m-%Y').date()

            salesOrder.payment_method = None if request.POST['payment_method'] == "" else request.POST['payment_method']
            salesOrder.cheque_no = None if request.POST['cheque_id'] == "" else request.POST['cheque_id']
            salesOrder.upi_no = None if request.POST['upi_id'] == "" else request.POST['upi_id']
            salesOrder.bank_acc_no = None if request.POST['bnk_id'] == "" else request.POST['bnk_id']

            salesOrder.subtotal = 0.0 if request.POST['subtotal'] == "" else float(request.POST['subtotal'])
            salesOrder.igst = 0.0 if request.POST['igst'] == "" else float(request.POST['igst'])
            salesOrder.cgst = 0.0 if request.POST['cgst'] == "" else float(request.POST['cgst'])
            salesOrder.sgst = 0.0 if request.POST['sgst'] == "" else float(request.POST['sgst'])
            salesOrder.tax_amount = 0.0 if request.POST['taxamount'] == "" else float(request.POST['taxamount'])
            salesOrder.adjustment = 0.0 if request.POST['adj'] == "" else float(request.POST['adj'])
            salesOrder.shipping_charge = 0.0 if request.POST['ship'] == "" else float(request.POST['ship'])
            salesOrder.grandtotal = 0.0 if request.POST['grandtotal'] == "" else float(request.POST['grandtotal'])
            salesOrder.paid_off = 0.0 if request.POST['advance'] == "" else float(request.POST['advance'])
            salesOrder.balance = request.POST['grandtotal'] if request.POST['balance'] == "" else float(request.POST['balance'])

            salesOrder.note = request.POST['note']

            if len(request.FILES) != 0:
                salesOrder.file=request.FILES.get('file')

            salesOrder.save()

            # Save invoice items.

            itemId = request.POST.getlist("item_id[]")
            itemName = request.POST.getlist("item_name[]")
            hsn  = request.POST.getlist("hsn[]")
            qty = request.POST.getlist("qty[]")
            price = request.POST.getlist("priceListPrice[]") if 'priceList' in request.POST else request.POST.getlist("price[]")
            tax = request.POST.getlist("taxGST[]") if request.POST['place_of_supply'] == com.State else request.POST.getlist("taxIGST[]")
            discount = request.POST.getlist("discount[]")
            total = request.POST.getlist("total[]")
            so_item_ids = request.POST.getlist("id[]")
            SOItem_ids = [int(id) for id in so_item_ids]

            order_items = Fin_Sales_Order_Items.objects.filter(SalesOrder = salesOrder)
            object_ids = [obj.id for obj in order_items]

            ids_to_delete = [obj_id for obj_id in object_ids if obj_id not in SOItem_ids]

            Fin_Sales_Order_Items.objects.filter(id__in=ids_to_delete).delete()
            
            count = Fin_Sales_Order_Items.objects.filter(SalesOrder = salesOrder).count()

            if len(itemId)==len(itemName)==len(hsn)==len(qty)==len(price)==len(tax)==len(discount)==len(total)==len(SOItem_ids) and SOItem_ids and itemId and itemName and hsn and qty and price and tax and discount and total:
                mapped = zip(itemId,itemName,hsn,qty,price,tax,discount,total,SOItem_ids)
                mapped = list(mapped)
                for ele in mapped:
                    if int(len(itemId))>int(count):
                        if ele[8] == 0:
                            itm = Fin_Items.objects.get(id = int(ele[0]))
                            Fin_Sales_Order_Items.objects.create(SalesOrder = salesOrder, Item = itm, hsn = ele[2], quantity = int(ele[3]), price = float(ele[4]), tax = ele[5], discount = float(ele[6]), total = float(ele[7]))
                        else:
                            itm = Fin_Items.objects.get(id = int(ele[0]))
                            Fin_Sales_Order_Items.objects.filter( id = int(ele[8])).update(SalesOrder = salesOrder, Item = itm, hsn = ele[2], quantity = int(ele[3]), price = float(ele[4]), tax = ele[5], discount = float(ele[6]), total = float(ele[7]))
                    else:
                        itm = Fin_Items.objects.get(id = int(ele[0]))
                        Fin_Sales_Order_Items.objects.filter( id = int(ele[8])).update(SalesOrder = salesOrder, Item = itm, hsn = ele[2], quantity = int(ele[3]), price = float(ele[4]), tax = ele[5], discount = float(ele[6]), total = float(ele[7]))
            
            # Save transaction
                    
            Fin_Sales_Order_History.objects.create(
                Company = com,
                LoginDetails = data,
                SalesOrder = salesOrder,
                action = 'Edited'
            )

            return redirect(Fin_viewSalesOrder, id)
        else:
            return redirect(Fin_editSalesOrder, id)
    else:
       return redirect('/')

def Fin_attachSalesOrderFile(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        salesOrder = Fin_Sales_Order.objects.get(id = id)

        if request.method == 'POST' and len(request.FILES) != 0:
            salesOrder.file = request.FILES.get('file')
            salesOrder.save()

        return redirect(Fin_viewSalesOrder, id)
    else:
        return redirect('/')

def Fin_salesOrderPdf(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        salesOrder = Fin_Sales_Order.objects.get(id = id)
        itms = Fin_Sales_Order_Items.objects.filter(SalesOrder = salesOrder)
    
        context = {'order':salesOrder, 'orderItems':itms,'cmp':com}
        
        template_path = 'company/Fin_Sales_Order_Pdf.html'
        fname = 'Sales_Order_'+salesOrder.sales_order_no
        # return render(request, 'company/Fin_Invoice_Pdf.html',context)
        # Create a Django response object, and specify content_type as pdftemp_
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] =f'attachment; filename = {fname}.pdf'
        # find the template and render it.
        template = get_template(template_path)
        html = template.render(context)

        # create a pdf
        pisa_status = pisa.CreatePDF(
        html, dest=response)
        # if error then show some funny view
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
    else:
        return redirect('/')

def Fin_shareSalesOrderToEmail(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        salesOrder = Fin_Sales_Order.objects.get(id = id)
        itms = Fin_Sales_Order_Items.objects.filter(SalesOrder = salesOrder)
        try:
            if request.method == 'POST':
                emails_string = request.POST['email_ids']

                # Split the string by commas and remove any leading or trailing whitespace
                emails_list = [email.strip() for email in emails_string.split(',')]
                email_message = request.POST['email_message']
                # print(emails_list)
            
                context = {'order':salesOrder, 'orderItems':itms,'cmp':com}
                template_path = 'company/Fin_Sales_Order_Pdf.html'
                template = get_template(template_path)

                html  = template.render(context)
                result = BytesIO()
                pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
                pdf = result.getvalue()
                filename = f'Sales_Order_{salesOrder.sales_order_no}'
                subject = f"Sales_Order_{salesOrder.sales_order_no}"
                email = EmailMessage(subject, f"Hi,\nPlease find the attached Sales Order for - #-{salesOrder.sales_order_no}. \n{email_message}\n\n--\nRegards,\n{com.Company_name}\n{com.Address}\n{com.State} - {com.Country}\n{com.Contact}", from_email=settings.EMAIL_HOST_USER, to=emails_list)
                email.attach(filename, pdf, "application/pdf")
                email.send(fail_silently=False)

                messages.success(request, 'Sales Order details has been shared via email successfully..!')
                return redirect(Fin_viewSalesOrder,id)
        except Exception as e:
            print(e)
            messages.error(request, f'{e}')
            return redirect(Fin_viewSalesOrder, id)

def Fin_convertSalesOrderToInvoice(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            cmp = com
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            cmp = com.company_id

        salesOrder = Fin_Sales_Order.objects.get(id = id)
        orderItms = Fin_Sales_Order_Items.objects.filter(SalesOrder = salesOrder)
        cust = Fin_Customers.objects.filter(Company = cmp, status = 'Active')
        itms = Fin_Items.objects.filter(Company = cmp, status = 'Active')
        trms = Fin_Company_Payment_Terms.objects.filter(Company = cmp)
        bnk = Fin_Banking.objects.filter(company = cmp)
        lst = Fin_Price_List.objects.filter(Company = cmp, status = 'Active')
        units = Fin_Units.objects.filter(Company = cmp)
        acc = Fin_Chart_Of_Account.objects.filter(Q(account_type='Expense') | Q(account_type='Other Expense') | Q(account_type='Cost Of Goods Sold'), Company=cmp).order_by('account_name')

        # Fetching last invoice and assigning upcoming ref no as current + 1
        # Also check for if any bill is deleted and ref no is continuos w r t the deleted invoice
        latest_inv = Fin_Invoice.objects.filter(Company = cmp).order_by('-id').first()

        new_number = int(latest_inv.reference_no) + 1 if latest_inv else 1

        if Fin_Invoice_Reference.objects.filter(Company = cmp).exists():
            deleted = Fin_Invoice_Reference.objects.get(Company = cmp)
            
            if deleted:
                while int(deleted.reference_no) >= new_number:
                    new_number+=1

        # Finding next invoice number w r t last invoic number if exists.
        nxtInv = ""
        lastInv = Fin_Invoice.objects.filter(Company = cmp).last()
        if lastInv:
            inv_no = str(lastInv.invoice_no)
            numbers = []
            stri = []
            for word in inv_no:
                if word.isdigit():
                    numbers.append(word)
                else:
                    stri.append(word)
            
            num=''
            for i in numbers:
                num +=i
            
            st = ''
            for j in stri:
                st = st+j

            inv_num = int(num)+1

            if num[0] == '0':
                if inv_num <10:
                    nxtInv = st+'0'+ str(inv_num)
                else:
                    nxtInv = st+ str(inv_num)
            else:
                nxtInv = st+ str(inv_num)

        context = {
            'allmodules':allmodules, 'com':com, 'cmp':cmp, 'data':data,'order':salesOrder, 'orderItems':orderItms, 'customers':cust, 'items':itms, 'pTerms':trms,'list':lst,
            'banks':bnk,'units':units, 'accounts':acc,'ref_no':new_number,'invNo':nxtInv
        }
        return render(request,'company/Fin_Convert_SalesOrder_toInvoice.html',context)
    else:
       return redirect('/')

def Fin_salesOrderConvertInvoice(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        salesOrder = Fin_Sales_Order.objects.get(id = id)
        if request.method == 'POST':
            invNum = request.POST['invoice_no']
            if Fin_Invoice.objects.filter(Company = com, invoice_no__iexact = invNum).exists():
                res = f'<script>alert("Invoice Number `{invNum}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)

            inv = Fin_Invoice(
                Company = com,
                LoginDetails = com.Login_Id,
                Customer = Fin_Customers.objects.get(id = request.POST['customer']),
                customer_email = request.POST['customerEmail'],
                billing_address = request.POST['bill_address'],
                gst_type = request.POST['gst_type'],
                gstin = request.POST['gstin'],
                place_of_supply = request.POST['place_of_supply'],
                reference_no = request.POST['reference_number'],
                invoice_no = invNum,
                payment_terms = Fin_Company_Payment_Terms.objects.get(id = request.POST['payment_term']),
                invoice_date = request.POST['invoice_date'],
                duedate = datetime.strptime(request.POST['due_date'], '%d-%m-%Y').date(),
                salesOrder_no = request.POST['order_number'],
                exp_ship_date = datetime.strptime(request.POST['due_date'], '%d-%m-%Y').date(),
                price_list_applied = True if 'priceList' in request.POST else False,
                payment_method = None if request.POST['payment_method'] == "" else request.POST['payment_method'],
                cheque_no = None if request.POST['cheque_id'] == "" else request.POST['cheque_id'],
                upi_no = None if request.POST['upi_id'] == "" else request.POST['upi_id'],
                bank_acc_no = None if request.POST['bnk_id'] == "" else request.POST['bnk_id'],
                subtotal = 0.0 if request.POST['subtotal'] == "" else float(request.POST['subtotal']),
                igst = 0.0 if request.POST['igst'] == "" else float(request.POST['igst']),
                cgst = 0.0 if request.POST['cgst'] == "" else float(request.POST['cgst']),
                sgst = 0.0 if request.POST['sgst'] == "" else float(request.POST['sgst']),
                tax_amount = 0.0 if request.POST['taxamount'] == "" else float(request.POST['taxamount']),
                adjustment = 0.0 if request.POST['adj'] == "" else float(request.POST['adj']),
                shipping_charge = 0.0 if request.POST['ship'] == "" else float(request.POST['ship']),
                grandtotal = 0.0 if request.POST['grandtotal'] == "" else float(request.POST['grandtotal']),
                paid_off = 0.0 if request.POST['advance'] == "" else float(request.POST['advance']),
                balance = request.POST['grandtotal'] if request.POST['balance'] == "" else float(request.POST['balance']),
                note = request.POST['note'],
                status = "Saved" 
            )

            inv.save()

            if len(request.FILES) != 0:
                inv.file=request.FILES.get('file')
            inv.save()

            # Save invoice items.

            itemId = request.POST.getlist("item_id[]")
            itemName = request.POST.getlist("item_name[]")
            hsn  = request.POST.getlist("hsn[]")
            qty = request.POST.getlist("qty[]")
            price = request.POST.getlist("priceListPrice[]") if 'priceList' in request.POST else request.POST.getlist("price[]")
            tax = request.POST.getlist("taxGST[]") if request.POST['place_of_supply'] == com.State else request.POST.getlist("taxIGST[]")
            discount = request.POST.getlist("discount[]")
            total = request.POST.getlist("total[]")

            if len(itemId)==len(itemName)==len(hsn)==len(qty)==len(price)==len(tax)==len(discount)==len(total) and itemId and itemName and hsn and qty and price and tax and discount and total:
                mapped = zip(itemId,itemName,hsn,qty,price,tax,discount,total)
                mapped = list(mapped)
                for ele in mapped:
                    itm = Fin_Items.objects.get(id = int(ele[0]))
                    Fin_Invoice_Items.objects.create(Invoice = inv, Item = itm, hsn = ele[2], quantity = int(ele[3]), price = float(ele[4]), tax = ele[5], discount = float(ele[6]), total = float(ele[7]))
                    itm.current_stock -= int(ele[3])
                    itm.save()
            
            # Save transaction
                    
            Fin_Invoice_History.objects.create(
                Company = com,
                LoginDetails = data,
                Invoice = inv,
                action = 'Created'
            )

            # Save invoice details to SalesOrder

            salesOrder.converted_to_invoice = inv
            salesOrder.save()

            return redirect(Fin_salesOrder)
        else:
            return redirect(Fin_convertSalesOrderToInvoice, id)
    else:
       return redirect('/')

def Fin_convertSalesOrderToRecInvoice(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            cmp = com
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            cmp = com.company_id

        salesOrder = Fin_Sales_Order.objects.get(id = id)
        orderItms = Fin_Sales_Order_Items.objects.filter(SalesOrder = salesOrder)

        cust = Fin_Customers.objects.filter(Company = cmp, status = 'Active')
        itms = Fin_Items.objects.filter(Company = cmp, status = 'Active')
        trms = Fin_Company_Payment_Terms.objects.filter(Company = cmp)
        bnk = Fin_Banking.objects.filter(company = cmp)
        lst = Fin_Price_List.objects.filter(Company = cmp, status = 'Active')
        units = Fin_Units.objects.filter(Company = cmp)
        acc = Fin_Chart_Of_Account.objects.filter(Q(account_type='Expense') | Q(account_type='Other Expense') | Q(account_type='Cost Of Goods Sold'), Company=cmp).order_by('account_name')
        repeat = Fin_CompanyRepeatEvery.objects.filter(company = cmp)
        priceList = Fin_Price_List.objects.filter(Company = cmp, type = 'Sales', status = 'Active')

        # Fetching last invoice and assigning upcoming ref no as current + 1
        # Also check for if any bill is deleted and ref no is continuos w r t the deleted invoice
        latest_inv = Fin_Recurring_Invoice.objects.filter(Company = cmp).order_by('-id').first()

        new_number = int(latest_inv.reference_no) + 1 if latest_inv else 1

        if Fin_Recurring_Invoice_Reference.objects.filter(Company = cmp).exists():
            deleted = Fin_Recurring_Invoice_Reference.objects.get(Company = cmp)
            
            if deleted:
                while int(deleted.reference_no) >= new_number:
                    new_number+=1

        # Finding next rec_invoice number w r t last rec_invoice number if exists.
        nxtInv = ""
        lastInv = Fin_Recurring_Invoice.objects.filter(Company = cmp).last()
        if lastInv:
            inv_no = str(lastInv.rec_invoice_no)
            numbers = []
            stri = []
            for word in inv_no:
                if word.isdigit():
                    numbers.append(word)
                else:
                    stri.append(word)
            
            num=''
            for i in numbers:
                num +=i
            
            st = ''
            for j in stri:
                st = st+j

            inv_num = int(num)+1

            if num[0] == '0':
                if inv_num <10:
                    nxtInv = st+'0'+ str(inv_num)
                else:
                    nxtInv = st+ str(inv_num)
            else:
                nxtInv = st+ str(inv_num)
        else:
            nxtInv = 'RI01'

        context = {
            'allmodules':allmodules, 'com':com, 'cmp':cmp, 'data':data,'order':salesOrder, 'orderItems':orderItms, 'customers':cust, 'items':itms, 'pTerms':trms,'list':lst,
            'banks':bnk,'units':units, 'accounts':acc,'ref_no':new_number,'invNo':nxtInv, 'priceListItems':priceList, 'repeat':repeat,
        }
        return render(request,'company/Fin_Convert_SalesOrder_toRecInvoice.html',context)
    else:
       return redirect('/')
       
def Fin_salesOrderConvertRecInvoice(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        salesOrder = Fin_Sales_Order.objects.get(id = id)

        if request.method == 'POST':
            invNum = request.POST['rec_invoice_no']
            if Fin_Recurring_Invoice.objects.filter(Company = com, rec_invoice_no__iexact = invNum).exists():
                res = f'<script>alert("Rec. Invoice Number `{invNum}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)

            inv = Fin_Recurring_Invoice(
                Company = com,
                LoginDetails = com.Login_Id,
                Customer = Fin_Customers.objects.get(id = request.POST['customerId']),
                customer_email = request.POST['customerEmail'],
                billing_address = request.POST['bill_address'],
                gst_type = request.POST['gst_type'],
                gstin = request.POST['gstin'],
                place_of_supply = request.POST['place_of_supply'],
                profile_name = request.POST['profile_name'],
                entry_type = None if request.POST['entry_type'] == "" else request.POST['entry_type'],
                reference_no = request.POST['reference_number'],
                rec_invoice_no = invNum,
                payment_terms = Fin_Company_Payment_Terms.objects.get(id = request.POST['payment_term']),
                start_date = request.POST['start_date'],
                end_date = datetime.strptime(request.POST['end_date'], '%d-%m-%Y').date(),
                salesOrder_no = request.POST['order_number'],
                price_list_applied = True if 'priceList' in request.POST else False,
                price_list = None if request.POST['price_list_id'] == "" else Fin_Price_List.objects.get(id = request.POST['price_list_id']),
                repeat_every = Fin_CompanyRepeatEvery.objects.get(id = request.POST['repeat_every']),
                payment_method = None if request.POST['payment_method'] == "" else request.POST['payment_method'],
                cheque_no = None if request.POST['cheque_id'] == "" else request.POST['cheque_id'],
                upi_no = None if request.POST['upi_id'] == "" else request.POST['upi_id'],
                bank_acc_no = None if request.POST['bnk_id'] == "" else request.POST['bnk_id'],
                subtotal = 0.0 if request.POST['subtotal'] == "" else float(request.POST['subtotal']),
                igst = 0.0 if request.POST['igst'] == "" else float(request.POST['igst']),
                cgst = 0.0 if request.POST['cgst'] == "" else float(request.POST['cgst']),
                sgst = 0.0 if request.POST['sgst'] == "" else float(request.POST['sgst']),
                tax_amount = 0.0 if request.POST['taxamount'] == "" else float(request.POST['taxamount']),
                adjustment = 0.0 if request.POST['adj'] == "" else float(request.POST['adj']),
                shipping_charge = 0.0 if request.POST['ship'] == "" else float(request.POST['ship']),
                grandtotal = 0.0 if request.POST['grandtotal'] == "" else float(request.POST['grandtotal']),
                paid_off = 0.0 if request.POST['advance'] == "" else float(request.POST['advance']),
                balance = request.POST['grandtotal'] if request.POST['balance'] == "" else float(request.POST['balance']),
                note = request.POST['note']
            )

            inv.save()

            if len(request.FILES) != 0:
                inv.file=request.FILES.get('file')
            inv.save()

            if 'Draft' in request.POST:
                inv.status = "Draft"
            elif "Save" in request.POST:
                inv.status = "Saved" 
            inv.save()

            # Save rec_invoice items.

            itemId = request.POST.getlist("item_id[]")
            itemName = request.POST.getlist("item_name[]")
            hsn  = request.POST.getlist("hsn[]")
            qty = request.POST.getlist("qty[]")
            price = request.POST.getlist("priceListPrice[]") if 'priceList' in request.POST else request.POST.getlist("price[]")
            tax = request.POST.getlist("taxGST[]") if request.POST['place_of_supply'] == com.State else request.POST.getlist("taxIGST[]")
            discount = request.POST.getlist("discount[]")
            total = request.POST.getlist("total[]")

            if len(itemId)==len(itemName)==len(hsn)==len(qty)==len(price)==len(tax)==len(discount)==len(total) and itemId and itemName and hsn and qty and price and tax and discount and total:
                mapped = zip(itemId,itemName,hsn,qty,price,tax,discount,total)
                mapped = list(mapped)
                for ele in mapped:
                    itm = Fin_Items.objects.get(id = int(ele[0]))
                    Fin_Recurring_Invoice_Items.objects.create(RecInvoice = inv, Item = itm, hsn = ele[2], quantity = int(ele[3]), price = float(ele[4]), tax = ele[5], discount = float(ele[6]), total = float(ele[7]))
                    itm.current_stock -= int(ele[3])
                    itm.save()
            
            # Save transaction
                    
            Fin_Recurring_Invoice_History.objects.create(
                Company = com,
                LoginDetails = data,
                RecInvoice = inv,
                action = 'Created'
            )

            # Save Rec Inv details to Sales Order

            salesOrder.converted_to_rec_invoice = inv
            salesOrder.save()

            return redirect(Fin_salesOrder)
        else:
            return redirect(Fin_convertSalesOrderToRecInvoice, id)
    else:
       return redirect('/')
# End


#  ----------------------------- TINTO VIEWS LOAN  sTART-----------------------------

    
def employee_loan_list(request):
    sid = request.session['s_id']
    login = Fin_Login_Details.objects.get(id=sid)
    if login.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        employee = Employee.objects.filter(company_id=com.id)
        loan = Fin_Loan.objects.filter(company_id=com.id)
    elif login.User_Type == 'Staff' :
        staf = Fin_Staff_Details.objects.get(Login_Id = sid)
        com=staf.company_id
        allmodules = Fin_Modules_List.objects.get(company_id = staf.company_id_id)
        
        employee = Employee.objects.filter(company_id=staf.company_id_id)
        loan = Fin_Loan.objects.filter(company_id=staf.company_id.id)
    else:
        distributor = Fin_Distributors_Details.objects.get(Login_Id = sid)

    return render(request,'company/Employee_loan_list.html',{'employee':employee,'allmodules':allmodules,'loan':loan,'com':com})

def employee_loan_sort_by_balance(request):
    sid = request.session['s_id']
    login = Fin_Login_Details.objects.get(id=sid)
    if login.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        employee = Employee.objects.filter(company_id=com.id)
        loan = Fin_Loan.objects.filter(company_id=com.id).order_by('-balance')

    elif login.User_Type == 'Staff' :
        staf = Fin_Staff_Details.objects.get(Login_Id = sid)
        com=staf.company_id
        allmodules = Fin_Modules_List.objects.get(company_id = staf.company_id_id)
        employee = Employee.objects.filter(company_id=staf.company_id_id)
        loan = Fin_Loan.objects.filter(company_id=com.id).order_by('-balance')

    else:
        distributor = Fin_Distributors_Details.objects.get(Login_Id = sid)

    return render(request,'company/Employee_loan_list.html',{'employee':employee,'allmodules':allmodules,'loan':loan,'com':com})


def employee_loan_sort_by_employeename(request):
    sid = request.session['s_id']
    login = Fin_Login_Details.objects.get(id=sid)
    if login.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        employee = Employee.objects.filter(company_id=com.id)
        loan = Fin_Loan.objects.filter(company_id=com.id).order_by('-employee_name')

    elif login.User_Type == 'Staff' :
        staf = Fin_Staff_Details.objects.get(Login_Id = sid)
        com=staf.company_id
        allmodules = Fin_Modules_List.objects.get(company_id = staf.company_id_id)
        employee = Employee.objects.filter(company_id=staf.company_id_id)
        loan = Fin_Loan.objects.filter(company_id=com.id).order_by('-employee_name')

    else:
        distributor = Fin_Distributors_Details.objects.get(Login_Id = sid)

    return render(request,'company/Employee_loan_list.html',{'employee':employee,'allmodules':allmodules,'loan':loan,'com':com})

def employee_loan_filter_by_active(request):
    sid = request.session['s_id']
    login = Fin_Login_Details.objects.get(id=sid)
    if login.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        employee = Employee.objects.filter(company_id=com.id)
        loan = Fin_Loan.objects.filter(company_id=com.id,status='Active')

    elif login.User_Type == 'Staff' :
        staf = Fin_Staff_Details.objects.get(Login_Id = sid)
        com=staf.company_id
        allmodules = Fin_Modules_List.objects.get(company_id = staf.company_id_id)
        employee = Employee.objects.filter(company_id=staf.company_id_id)
        loan = Fin_Loan.objects.filter(company_id=staf.company_id_id,status='Active')

    else:
        distributor = Fin_Distributors_Details.objects.get(Login_Id = sid)

    return render(request,'company/Employee_loan_list.html',{'employee':employee,'allmodules':allmodules,'loan':loan,'com':com})

def employee_loan_filter_by_inactive(request):
    sid = request.session['s_id']
    login = Fin_Login_Details.objects.get(id=sid)
    if login.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        employee = Employee.objects.filter(company_id=com.id)
        loan = Fin_Loan.objects.filter(company_id=com.id,status='Inactive')

    elif login.User_Type == 'Staff' :
        staf = Fin_Staff_Details.objects.get(Login_Id = sid)
        com=staf.company_id
        allmodules = Fin_Modules_List.objects.get(company_id = staf.company_id_id)
        employee = Employee.objects.filter(company_id=staf.company_id_id)
        loan = Fin_Loan.objects.filter(company_id=staf.company_id_id,status='Inactive')

    else:
        distributor = Fin_Distributors_Details.objects.get(Login_Id = sid)

    return render(request,'company/Employee_loan_list.html',{'employee':employee,'allmodules':allmodules,'loan':loan,'com':com})

def employee_loan_create_page(request):
    sid = request.session['s_id']
    login = Fin_Login_Details.objects.get(id=sid)
    
    if login.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        employee = Employee.objects.filter(company_id=com.id,employee_status='Active')
        term=Fin_Loan_Term.objects.filter(company=com)
        
        banks=Fin_Banking.objects.filter(company=com)
        bloodgroup = Employee_Blood_Group.objects.filter(company_id=com.id,login_id=sid).values('blood_group').distinct()
      
        
    elif login.User_Type == 'Staff' :
        staf = Fin_Staff_Details.objects.get(Login_Id = sid)
        com=staf.company_id
        allmodules = Fin_Modules_List.objects.get(company_id = staf.company_id_id)
        employee = Employee.objects.filter(company_id=staf.company_id_id,employee_status='Active')
        term=Fin_Loan_Term.objects.filter(company=staf.company_id)
        banks=Fin_Banking.objects.filter(company=staf.company_id)
        bloodgroup = Employee_Blood_Group.objects.filter(company_id=com.id,login_id=sid).values('blood_group').distinct()
      

    return render(request,'company/Employee_loan_create.html',{'allmodules':allmodules,'employee':employee,'term':term,'banks':banks,'com':com,'bloodgroup':bloodgroup})    

def employeedata(request):
    sid = request.session['s_id']
    login = Fin_Login_Details.objects.get(id=sid)
    
    if login.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        customer_id = request.GET.get('id')
        cust = Employee.objects.get(id=customer_id,company_id=com.id)
        data7 = {'email': cust.employee_mail,'salary':cust.salary_amount,'jdate':cust.date_of_joining,'empid':cust.employee_number}
        return JsonResponse(data7)

      
        
    elif login.User_Type == 'Staff' :
        staf = Fin_Staff_Details.objects.get(Login_Id = sid)
        customer_id = request.GET.get('id')
        cust = Employee.objects.get(id=customer_id,company_id=staf.company_id_id)
        data7 = {'email': cust.employee_mail,'salary':cust.salary_amount,'jdate':cust.date_of_joining,'empid':cust.employee_number}
        return JsonResponse(data7)


def termdata(request):
    sid = request.session['s_id']
    login = Fin_Login_Details.objects.get(id=sid)
    
    if login.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        customer_id = request.GET.get('id')
        cust = Fin_Loan_Term.objects.get(id=customer_id,company_id=com.id)
        data7 = {'days': cust.days}
        return JsonResponse(data7)

      
        
    elif login.User_Type == 'Staff' :
        staf = Fin_Staff_Details.objects.get(Login_Id = sid)
        customer_id = request.GET.get('id')
        cust = Fin_Loan_Term.objects.get(id=customer_id,company_id=staf.company_id_id)
        data7 = {'days': cust.days}
        return JsonResponse(data7)


def employee_loan_save(request):


    

    if request.method == 'POST':


        employeename = request.POST['employee']
        empid = request.POST['empid']
        empemail = request.POST['empemail']
        salary = request.POST['salary']
        join_date = request.POST['Joining_Date']

        loan_Date = request.POST.get('loan_date1', None)
        loan_amount = request.POST['loan_amount']
        loanduration = request.POST['loanduration']
        duration=Fin_Loan_Term.objects.get(id=loanduration)
        

        expdate = request.POST['expdate']
        select_payment = request.POST['select_payment']
        if select_payment!="Cash" and "UPI" and "Cheque":
            select="Bank"
        else:
            select=select_payment

        
        cheque_no = request.POST['cheque_no']
        upi_id = request.POST['upi_id']
        acc_no = request.POST['acc_no']
        cutingamount = request.POST['cutingamount']
        cp = request.POST['cuttingPercentage']
        if cp != '':
            cuttingPercentage=cp
        elif cp == '':
            cuttingPercentage=0

        amount1 = request.POST['pamount']
        amount2 = request.POST['amount5']
        if amount1 != '':
            amount=amount1
        elif amount2 != '':
            amount=amount2



        Note = request.POST['Note']
     
        file = request.FILES.get('File', None)
        if file:
            file = request.FILES['File']
        else:
            file=''
        
        sid = request.session['s_id']
        employee = Fin_Login_Details.objects.get(id=sid)
        
        emp=Employee.objects.get(id=employeename)
        
        if employee.User_Type == 'Company':
                    companykey =  Fin_Company_Details.objects.get(Login_Id_id=sid)
                    if Fin_Loan.objects.filter(employeeid=empid, company=companykey).exists():
                        messages.error(request,'Already a loan  exsits for this employee !!!')
                        return redirect('employee_loan_create_page')
                    else:
                

                            new = Fin_Loan(employee=emp,employeeid=empid,employee_email=empemail,salary=salary,join_date=join_date,loan_date=loan_Date,loan_amount=loan_amount,total_loan=loan_amount,
                                    expiry_date=expdate,payment_method=select,cheque_number=cheque_no,upi_id=upi_id,bank_account=acc_no,monthly_cutting_percentage=cuttingPercentage,loan_duration=duration,
                                    monthly_cutting_amount=amount,note=Note,attach_file=file,company=companykey,login_details=employee,balance=loan_amount,employee_name =emp.title +" " + emp.first_name + " " + emp.last_name,monthly_cutting=cutingamount)
                            
                                
                            new.save()

                            com = Fin_Loan.objects.get(id=new.id)
                            history = Fin_Employee_Loan_History(company = companykey,login_details=employee,employee_loan =com,date = date.today(),action = 'Created')
                            history.save()
                            trans = Fin_Employee_Loan_Transactions(company = companykey,login_details=employee,employee_loan =com,date = date.today(),particulars = 'LOAN ISSUED',employee=emp,balance=loan_amount)
                            trans.save()
                            t = Fin_Employee_Loan_Transactions.objects.get(id=trans.id)
                            trans2 = Fin_Employee_Loan_Transactions_History(company = companykey,login_details=employee,employee_loan =com,date = date.today(),action = 'Created',transaction=t)
                            trans2.save()
        
        elif employee.User_Type == 'Staff':
                staf = Fin_Staff_Details.objects.get(Login_Id = sid)
                if Fin_Loan.objects.filter(employeeid=empid, company=staf.company_id).exists():
                        messages.error(request,'Already a loan  exsits for this employee !!!')
                        return redirect('employee_loan_create_page')
                else:
                

                        new =  Fin_Loan(employee=emp,employeeid=empid,employee_email=empemail,salary=salary,join_date=join_date,loan_date=loan_Date,loan_amount=loan_amount,total_loan=loan_amount,
                                expiry_date=expdate,payment_method=select,cheque_number=cheque_no,upi_id=upi_id,bank_account=acc_no,monthly_cutting_percentage=cuttingPercentage,loan_duration=duration,
                                monthly_cutting_amount=amount,note=Note,attach_file=file,company=staf.company_id,login_details=employee,balance=loan_amount,employee_name =emp.title +" " + emp.first_name + " " + emp.last_name,monthly_cutting=cutingamount)
                        
                        new.save()
                        com = Fin_Loan.objects.get(id=new.id)
                        history = Fin_Employee_Loan_History(company = staf.company_id,login_details=employee,employee_loan = com,date = timezone.now(),action = 'Created')
                        history.save()
                        trans = Fin_Employee_Loan_Transactions(company = staf.company_id,login_details=employee,employee_loan =com,date = date.today(),particulars = 'LOAN ISSUED',employee=emp,balance=loan_amount)
                        trans.save()
                        t = Fin_Employee_Loan_Transactions.objects.get(id=trans.id)
                        trans2 = Fin_Employee_Loan_Transactions_History(company = staf.company_id,login_details=employee,employee_loan =com,date = date.today(),action = 'Created',transaction=t)
                        trans2.save()

   
        return redirect(employee_loan_list)
    

def emploanoverview(request,pk):
    sid = request.session['s_id']
    login = Fin_Login_Details.objects.get(id=sid)
    
    if login.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        loan = Fin_Loan.objects.get(id=pk)
        est_comments = Fin_Employee_loan_comments.objects.filter(employee_loan=loan)
        employee = Employee.objects.get(id=loan.employee.id)
        trans=Fin_Employee_Loan_Transactions.objects.filter(employee_loan=loan)
        last_transaction = trans.last()
        balance=last_transaction.balance
        print(balance)

        latest_item_id=Fin_Employee_Loan_History.objects.filter(employee_loan=loan,company=com)
        latest_date = Fin_Employee_Loan_History.objects.filter(employee_loan=loan,company=com).aggregate(latest_date=Max('date'))['latest_date']  
        filtered_data = Fin_Employee_Loan_History.objects.get(date=latest_date, employee_loan=loan)
      
        
    elif login.User_Type == 'Staff' :
        staf = Fin_Staff_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = staf.company_id_id)
        employee = Employee.objects.filter(company_id=staf.company_id_id)
        com=staf.company_id
        loan = Fin_Loan.objects.get(id=pk)
        est_comments = Fin_Employee_loan_comments.objects.filter(employee_loan=loan)
        trans=Fin_Employee_Loan_Transactions.objects.filter(employee_loan=loan)
        last_transaction = trans.last()
        balance=last_transaction.balance
        latest_item_id=Fin_Employee_Loan_History.objects.filter(employee_loan=loan,company=staf.company_id)
        latest_date = Fin_Employee_Loan_History.objects.filter(employee_loan=loan,company=staf.company_id).aggregate(latest_date=Max('date'))['latest_date']  
        filtered_data = Fin_Employee_Loan_History.objects.get(date=latest_date, employee_loan=loan)
      

    return render(request,'company/employee_loan_overview.html',{'allmodules':allmodules,'loan':loan,'employee':employee,'trans':trans,'est_comments':est_comments,'latest_item_id':latest_item_id,'filtered_data':filtered_data,'com':com,'balance':balance})    

        
def emploanedit(request, pk):                                                                #new by tinto mt
  
    sid = request.session['s_id']
    login = Fin_Login_Details.objects.get(id=sid)

    
    # Retrieve the chart of accounts entry
    # loan = get_object_or_404(Loan, id=pk)
    

    # Check if 'company_id' is in the session

   
    if login.User_Type == 'Company':
      
     
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com)
        loan = Fin_Loan.objects.get(id=pk)
        employee = Employee.objects.filter(company=com)
        term=Fin_Loan_Term.objects.filter(company=com)
        banks=Fin_Banking.objects.filter(company=com)
        context = {
                    'allmodules':allmodules,
                    'loan':loan,
                    'employee':employee,
                    'term':term,
                    'banks':banks,
                    'com':com
            }
       
    
        
        if request.method=='POST':
        
    
        

            loan = Fin_Loan.objects.get(id=pk)
            d=Fin_Employee_Loan_Transactions.objects.get(employee_loan=pk,particulars='LOAN ISSUED')
            newloan=request.POST.get("loan_amount",None)
            if int(newloan)>int(d.balance):
                bal=int(newloan)-int(d.balance)
                # d.balance=d.balance+bal
                d.save()
                loan_trans = Fin_Employee_Loan_Transactions.objects.filter(Q(employee_loan=d.employee_loan) & Q(id__gte=d.id))
                print("s")
                loan.balance=loan.balance+bal
                for i in loan_trans:
                        print(i.balance)
                    
                        i.balance=i.balance+bal
                        last_balance=i.balance
                        i.save()
                        print(i.balance)

                        print("s3")
                        print(loan.balance)
    #             if last_balance is not None:
    #                 loans= Fin_Loan.objects.get(id=pk)
    # # Assuming you have an object where you want to save the last balance, let's call it 'loan_object'
    #                 loans.balance = last_balance
                
            if int(newloan)<int(d.balance):
                bal=int(d.balance)-int(newloan)
                # d.balance=d.balance-bal
                loan.balance=loan.balance-bal
                d.save()
                loan_trans = Fin_Employee_Loan_Transactions.objects.filter(Q(employee_loan=d.employee_loan) & Q(id__gte=d.id))
                print("s")
                for i in loan_trans:
                        print(i.balance)
                    
                        i.balance=i.balance-bal
                        last_balance=i.balance
                        i.save()
                        print(i.balance)
                        print("s3")
    #             if last_balance is not None:
    #                 loans= Fin_Loan.objects.get(id=pk)
    # # Assuming you have an object where you want to save the last balance, let's call it 'loan_object'
    #                 loans.balance = last_balance

            b=Fin_Employee_Loan_History()
            # c=Fin_Employee_Loan_Transactions.objects.get(employee_loan=pk)
            # c.balance=request.POST.get("loan_amount",None)
            t=Fin_Employee_Loan_Transactions_History()

            t.company=com
            t.login_details=login
            t.action="Edited"
            t.date=date.today()
            t.transaction=d
            t.employee_loan=loan

            t.save()
            # c.save()
            b.company=com
            b.login_details=login
            b.action="Edited"
            b.date=date.today()
   
        
            loan.login_details=login
            loan.company=com
            emp=request.POST["employee"]
            emp1=Employee.objects.get(id=emp)
            employee_name1 =emp1.title +" " + emp1.first_name + " " + emp1.last_name
            loan.employee_name = employee_name1
            
            
            loanduration=request.POST.get("loanduration",None)
            term=Fin_Loan_Term.objects.get(id=loanduration)
            loan.loan_duration=term
            loan.employeeid = request.POST.get("empid",None)
            loan.employee_email = request.POST.get("empemail",None)
            loan.salary=request.POST.get("salary",None)
            loan.join_date=request.POST.get("join_date",None)
            loan.loan_date=request.POST.get("loan_date",None)
            loan.loan_amount=request.POST.get("loan_amount",None)
            loan.expiry_date=request.POST.get("expdate",None)
            loan.payment_method=request.POST.get("select_payment",None)
            loan.cheque_number=request.POST.get("cheque_no",None)
            loan.upi_id=request.POST.get("upi_id",None)
            loan.bank_account=request.POST.get("acc_no",None)
            loan.monthly_cutting=request.POST.get("cutingamount",None)
            if request.POST.get("cutingamount",None) == 'Yes':
                loan.monthly_cutting_percentage = 0
            else:
                loan.monthly_cutting_percentage=request.POST.get("cuttingPercentage",None)
            loan.monthly_cutting_amount=request.POST.get("monthly_cutting_amount",None)
            loan.bank_account=request.POST.get("acc_no",None)
            loan.monthly_cutting=request.POST.get("cutingamount",None)
            loan.monthly_cutting_percentage=request.POST.get("cuttingPercentage",None)
            amount1 = request.POST['pamount']
            amount2 = request.POST['amount5']
            if amount1 != '':
                loan.monthly_cutting_amount=amount1
            elif amount2 != '':
                loan.monthly_cutting_amount=amount2
            
            loan.note=request.POST.get('Note')
            loan.attach_file = request.FILES.get('File', None)
            loan.save()
            t=Fin_Loan.objects.get(id=loan.id)
            b.employee_loan=t
            b.save()
            current_utc_time = datetime.now(timezone.utc)
            history=Fin_Employee_Loan_History(company = com,login_details=login,employee_loan = loan,date = current_utc_time,action = 'Edited')
            history.save()
            # Save the changes
        
            # Redirect to another page after successful update
            return redirect('emploanoverview',loan.id)
        return render(request, 'company/Employee_loan_edit.html',context)
    if login.User_Type == 'Staff':
        # com = Fin_Company_Details.objects.get(Login_Id = sid)
        staf = Fin_Staff_Details.objects.get(Login_Id = sid)
        com = staf.company_id
        allmodules = Fin_Modules_List.objects.get(company_id = staf.company_id.id)
        loan = Fin_Loan.objects.get(id=pk)
        employee = Employee.objects.filter(company=staf.company_id)
        term=Fin_Loan_Term.objects.filter(company=staf.company_id)
        banks=Fin_Banking.objects.filter(company=staf.company_id)
        context = {
                    'allmodules':allmodules,
                    'loan':loan,
                    'employee':employee,
                    'term':term,
                    'banks':banks,
                    'com':com
            }
       
    
        
        if request.method=='POST':
        
    
        

            loan = Fin_Loan.objects.get(id=pk)
            d=Fin_Employee_Loan_Transactions.objects.get(employee_loan=pk,particulars='LOAN ISSUED')
            newloan=request.POST.get("loan_amount",None)
            if int(newloan)>int(d.balance):
                bal=int(newloan)-int(d.balance)
                # d.balance=d.balance+bal
                d.save()
                loan_trans = Fin_Employee_Loan_Transactions.objects.filter(Q(employee_loan=d.employee_loan) & Q(id__gte=d.id))
                print("s")
                loan.balance=loan.balance+bal
                for i in loan_trans:
                        print(i.balance)
                    
                        i.balance=i.balance+bal
                        last_balance=i.balance
                        i.save()
                        print(i.balance)

                        print("s3")
                        print(loan.balance)
    #             if last_balance is not None:
    #                 loans= Fin_Loan.objects.get(id=pk)
    # # Assuming you have an object where you want to save the last balance, let's call it 'loan_object'
    #                 loans.balance = last_balance
                
            if int(newloan)<int(d.balance):
                bal=int(d.balance)-int(newloan)
                # d.balance=d.balance-bal
                loan.balance=loan.balance-bal
                d.save()
                loan_trans = Fin_Employee_Loan_Transactions.objects.filter(Q(employee_loan=d.employee_loan) & Q(id__gte=d.id))
                print("s")
                for i in loan_trans:
                        print(i.balance)
                    
                        i.balance=i.balance-bal
                        last_balance=i.balance
                        i.save()
                        print(i.balance)
                        print("s3")
    #             if last_balance is not None:
    #                 loans= Fin_Loan.objects.get(id=pk)
    # # Assuming you have an object where you want to save the last balance, let's call it 'loan_object'
    #                 loans.balance = last_balance

            b=Fin_Employee_Loan_History()
            # c=Fin_Employee_Loan_Transactions.objects.get(employee_loan=pk)
            # c.balance=request.POST.get("loan_amount",None)
            t=Fin_Employee_Loan_Transactions_History()

            t.company=com
            t.login_details=login
            t.action="Edited"
            t.date=date.today()
            t.transaction=d
            t.employee_loan=loan

            t.save()
            # c.save()
            b.company=com
            b.login_details=login
            b.action="Edited"
            b.date=date.today()
   
        
            loan.login_details=login
            loan.company=com
            emp=request.POST["employee"]
            emp1=Employee.objects.get(id=emp)
            employee_name1 =emp1.title +" " + emp1.first_name + " " + emp1.last_name
            loan.employee_name = employee_name1
            
            
            loanduration=request.POST.get("loanduration",None)
            term=Fin_Loan_Term.objects.get(id=loanduration)
            loan.loan_duration=term
            loan.employeeid = request.POST.get("empid",None)
            loan.employee_email = request.POST.get("empemail",None)
            loan.salary=request.POST.get("salary",None)
            loan.join_date=request.POST.get("join_date",None)
            loan.loan_date=request.POST.get("loan_date",None)
            loan.loan_amount=request.POST.get("loan_amount",None)
            loan.expiry_date=request.POST.get("expdate",None)
            loan.payment_method=request.POST.get("select_payment",None)
            loan.cheque_number=request.POST.get("cheque_no",None)
            loan.upi_id=request.POST.get("upi_id",None)
            loan.bank_account=request.POST.get("acc_no",None)
            loan.monthly_cutting=request.POST.get("cutingamount",None)
            if request.POST.get("cutingamount",None) == 'Yes':
                loan.monthly_cutting_percentage = 0
            else:
                loan.monthly_cutting_percentage=request.POST.get("cuttingPercentage",None)
            loan.monthly_cutting_amount=request.POST.get("monthly_cutting_amount",None)
            loan.bank_account=request.POST.get("acc_no",None)
            loan.monthly_cutting=request.POST.get("cutingamount",None)
            loan.monthly_cutting_percentage=request.POST.get("cuttingPercentage",None)
            amount1 = request.POST['pamount']
            amount2 = request.POST['amount5']
            if amount1 != '':
                loan.monthly_cutting_amount=amount1
            elif amount2 != '':
                loan.monthly_cutting_amount=amount2
            
            loan.note=request.POST.get('Note')
            loan.attach_file = request.FILES.get('File', None)
            loan.save()
            t=Fin_Loan.objects.get(id=loan.id)
            b.employee_loan=t
            b.save()
            current_utc_time = datetime.now(timezone.utc)
            history=Fin_Employee_Loan_History(company = staf.company_id,login_details=login,employee_loan = loan,date = current_utc_time,action = 'Edited')
            history.save()
            # Save the changes
        
            # Redirect to another page after successful update
            return redirect('emploanoverview',loan.id)
        return render(request, 'company/Employee_loan_edit.html',context)

def emploanrepayment(request,pk):
    sid = request.session['s_id']
    login = Fin_Login_Details.objects.get(id=sid)
    
    if login.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        loan = Fin_Loan.objects.get(id=pk)
        employee = Employee.objects.get(id=loan.employee.id)
        trans=Fin_Employee_Loan_Transactions.objects.filter(employee=employee)
        banks=Fin_Banking.objects.filter(company=com)
      
        
    elif login.User_Type == 'Staff' :
        staf = Fin_Staff_Details.objects.get(Login_Id = sid)
        com=staf.company_id
        loan = Fin_Loan.objects.get(id=pk)
        allmodules = Fin_Modules_List.objects.get(company_id = staf.company_id_id)
        employee = Employee.objects.get(id=loan.employee.id)
        trans=Fin_Employee_Loan_Transactions.objects.filter(employee=loan.employee)
        banks=Fin_Banking.objects.filter(company=com)
      

    return render(request,'company/Employee_loan_repayment.html',{'allmodules':allmodules,'loan':loan,'employee':employee,'trans':trans,'com':com,'banks':banks})    


def emploanrepaymentsave(request,pk):
    sid = request.session['s_id']
    login = Fin_Login_Details.objects.get(id=sid)
    if login.User_Type == 'Company':

            if request.method == 'POST':


                principle_amount = request.POST['principal']
                interest= request.POST['interest']
                if interest == "":
                    interest_amount=0
                else:
                    interest_amount=interest
                principle_amount = request.POST['principal']
                payment_date= request.POST['date2']
                payment_method = request.POST['select_payment']
                total_amount= request.POST['total']
                cheque_number = request.POST['cheque_no']
                upi_id = request.POST['upi_id']
                bank_account= request.POST['acc_no']
                
                
                
            
                
                sid = request.session['s_id']
                employee = Fin_Login_Details.objects.get(id=sid)
                companykey =  Fin_Company_Details.objects.get(Login_Id=sid)
                loan=Fin_Loan.objects.get(id=pk)
                emp=Employee.objects.get(id=loan.employee.id)

                # last_transaction = Fin_Employee_Loan_Transactions.objects.get(employee_loan=pk).first()
                # Assuming principle_amount is a string, convert it to an integer
                principle_amount_int = int(principle_amount)

                # Perform the subtraction
                balance = loan.balance - principle_amount_int


                #transaction count 

                loan.transaction_count=loan.transaction_count+1
                
                

                
                loan.balance=balance
                loan.save()

        # Update the loan balance and save
        

        
                

                new = Fin_Employee_Loan_Repayment(employee=emp,company=companykey,login_details=employee,principle_amount=principle_amount,interest_amount=interest_amount,
                                              payment_date=payment_date,payment_method=payment_method,total_amount=total_amount,cheque_number=cheque_number,upi_id=upi_id,
                                              bank_account=bank_account,employee_loan=loan,balance=balance
                                              )
                new.save()
              

                com = Fin_Employee_Loan_Repayment.objects.get(id=new.id)
                # history = Employee_Loan_History(company = companykey,login_details=employee,employee_loan =com,date = date.today(),action = 'Created')
                # history.save()
                trans = Fin_Employee_Loan_Transactions(company = companykey,login_details=employee,employee_loan =loan,date = payment_date,particulars = 'EMI PAID',employee=emp,repayment=com,balance=balance)
                trans.save()
                t = Fin_Employee_Loan_Transactions.objects.get(id=trans.id)
                trans2 = Fin_Employee_Loan_Transactions_History(company = companykey,login_details=employee,repayment =com,date = payment_date,transaction=t,action='Created')
                trans2.save()
        
    elif login.User_Type == 'Staff':
            staf = Fin_Staff_Details.objects.get(Login_Id = sid)
            allmodules = Fin_Modules_List.objects.get(company_id = staf.company_id_id)
            employee = Employee.objects.filter(company_id=staf.company_id_id)
            com=staf.company_id
                

            if request.method == 'POST':


                principle_amount = request.POST['principal']
                interest= request.POST['interest']
                if interest == "":
                    interest_amount=0
                else:
                    interest_amount=interest
                principle_amount = request.POST['principal']
                payment_date= request.POST['date2']
                payment_method = request.POST['select_payment']
                total_amount= request.POST['total']
                cheque_number = request.POST['cheque_no']
                upi_id = request.POST['upi_id']
                bank_account= request.POST['acc_no']
                
                
                
            
                
                sid = request.session['s_id']
                employee = Fin_Login_Details.objects.get(id=sid)
              
                loan=Fin_Loan.objects.get(id=pk)
                emp=Employee.objects.get(id=loan.employee.id)
                # Assuming principle_amount is a string, convert it to an integer
                principle_amount_int = int(principle_amount)

                # Perform the subtraction
                balance = loan.balance - principle_amount_int
                
                
                #transaction count 

                loan.transaction_count=loan.transaction_count+1
                
                loan.balance=balance
                loan.save()

        # Update the loan balance and save
        

        
                

                new = Fin_Employee_Loan_Repayment(employee=emp,company=staf.company_id,login_details=employee,principle_amount=principle_amount,interest_amount=interest_amount,
                                              payment_date=payment_date,payment_method=payment_method,total_amount=total_amount,cheque_number=cheque_number,upi_id=upi_id,
                                              bank_account=bank_account,employee_loan=loan,balance=balance
                                              )
                new.save()
              

                com = Fin_Employee_Loan_Repayment.objects.get(id=new.id)
                # history = Employee_Loan_History(company = companykey,login_details=employee,employee_loan =com,date = date.today(),action = 'Created')
                # history.save()
                trans = Fin_Employee_Loan_Transactions(company = staf.company_id,login_details=employee,employee_loan =loan,date = payment_date,particulars = 'EMI PAID',employee=emp,repayment=com,balance=balance)
                trans.save()
                t = Fin_Employee_Loan_Transactions.objects.get(id=trans.id)
                trans2 = Fin_Employee_Loan_Transactions_History(company = staf.company_id,login_details=employee,repayment =com,date = payment_date,transaction=t,action='Created')
                trans2.save()

   
    return redirect(emploanoverview,pk)
    

def emploanrepaymentedit(request, pk):                                                                #new by tinto mt
  
    sid = request.session['s_id']
    login = Fin_Login_Details.objects.get(id=sid)

    
    # Retrieve the chart of accounts entry
    # loan = get_object_or_404(Loan, id=pk)
    

    # Check if 'company_id' is in the session

   
    if login.User_Type == 'Company':
      
     
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        
        loan_re = Fin_Employee_Loan_Repayment.objects.get(id=pk)
        loan = Fin_Loan.objects.get(id=loan_re.employee_loan.id)
        employee = Employee.objects.get(id=loan_re.employee.id)
        banks=Fin_Banking.objects.filter(company=com)
        context = {
                    'allmodules':allmodules,
                    'loan':loan,
                    'employee':employee,
                    'loan_re':loan_re,
                    'com':com,
                    'banks':banks
            }
       
    
        
        if request.method=='POST':
        
    
     
            loan1 = Fin_Employee_Loan_Repayment.objects.get(id=pk)
            c=Fin_Employee_Loan_Transactions.objects.get(repayment=loan1)
            loan2 = Fin_Loan.objects.get(id=loan_re.employee_loan.id)
            # t=Fin_Employee_Loan_Transactions_History()

            # t.company=com
            # t.login_details=login
            # t.action="Edited"
            # t.date=date.today()
            # t.transaction=c
            # t.repayment=loan1
            # t.employee_loan=loan2

            # t.save()
            
   
       
            loan1.login_details=login
            loan1.company=com
         
    
           
            

            previous_principle_amount=loan1.principle_amount
            previous_principle_amount=int(previous_principle_amount) #5000

            principle_amount=request.POST.get("principal",None)
            principle_amount_new=int(principle_amount)
            previousbalance=c.balance
            previousbalance=int(previousbalance)
            loan_trans = Fin_Employee_Loan_Transactions.objects.filter(Q(employee_loan=c.employee_loan) & Q(id__gte=c.id))
            print("s")
            for i in loan_trans:
                print(i.balance)
                print("s1")

            if previous_principle_amount<principle_amount_new:
                newprincipleamount=principle_amount_new-previous_principle_amount
                print("newprin")
                print(newprincipleamount)
                c.balance=c.balance-newprincipleamount
                loan2.balance=loan2.balance-newprincipleamount
                for i in loan_trans:
                    print(i.balance)
                  
                    i.balance=i.balance-newprincipleamount
                    i.save()
                    print(i.balance)
                    print("s3")
            if previous_principle_amount>principle_amount_new:
                newprincipleamount=previous_principle_amount-principle_amount_new
                print("newprin")
                print(newprincipleamount)
                c.balance=c.balance+newprincipleamount
                loan2.balance=loan2.balance+newprincipleamount
                for i in loan_trans:
                    print(i.balance)
                  
                    i.balance=i.balance+newprincipleamount
                    i.save()
                    print(i.balance)
                    print("s3")
        




            loan1.principle_amount=request.POST.get("principal",None)
            loan1.interest_amount=request.POST.get("interest",None)
            loan1.payment_date=request.POST.get("date",None)
            loan1.total_amount=request.POST.get("total",None)
            loan1.principle_amount=request.POST.get("principal",None)

            loan1.payment_method=request.POST.get("select_payment",None)
            loan1.cheque_number=request.POST.get("cheque_no",None)
            loan1.upi_id=request.POST.get("upi_id",None)
            loan1.bank_account=request.POST.get("acc_no",None)
            loan2.save()
            loan1.save()
            c.save()
            trans2 = Fin_Employee_Loan_Transactions_History(company =com ,login_details=login,repayment=loan1,date = date.today(),transaction=c,action='Edited')
            trans2.save()

            return redirect('emploanoverview',loan2.id)
        return render(request, 'company/Employee_loan_repayment_edit.html',context)
    if login.User_Type == 'Staff':
            staf = Fin_Staff_Details.objects.get(Login_Id = sid)
            com=staf.company_id
            allmodules = Fin_Modules_List.objects.get(company_id = staf.company_id_id)
            # employee = Employee.objects.filter(company_id=staf.company_id_id)
            allmodules = Fin_Modules_List.objects.get(company_id = staf.company_id_id)
            # loan = Loan.objects.get(id=pk)
            loan_re = Fin_Employee_Loan_Repayment.objects.get(id=pk)
            employee = Employee.objects.get(id=loan_re.employee.id)
            banks=Fin_Banking.objects.filter(company=com)
            context = {
                        'allmodules':allmodules,
                        # 'loan':loan,
                        'employee':employee,
                        'loan_re':loan_re,
                        'com':com,
                        'banks':banks
                }
        
        
            

        
            if request.method=='POST':
            
        
        
                loan1 = Fin_Employee_Loan_Repayment.objects.get(id=pk)
                c=Fin_Employee_Loan_Transactions.objects.get(repayment=loan1)
                loan2 = Fin_Loan.objects.get(id=loan_re.employee_loan.id)
                # t=Fin_Employee_Loan_Transactions_History()

                # t.company=com
                # t.login_details=login
                # t.action="Edited"
                # t.date=date.today()
                # t.transaction=c
                # t.repayment=loan1
                # t.employee_loan=loan2

                # t.save()
                
    
        
                loan1.login_details=login
                loan1.company=com
            
        
            
                

                previous_principle_amount=loan1.principle_amount
                previous_principle_amount=int(previous_principle_amount) #5000

                principle_amount=request.POST.get("principal",None)
                principle_amount_new=int(principle_amount)
                previousbalance=c.balance
                previousbalance=int(previousbalance)
                loan_trans = Fin_Employee_Loan_Transactions.objects.filter(Q(employee_loan=c.employee_loan) & Q(id__gte=c.id))
                print("s")
                for i in loan_trans:
                    print(i.balance)
                    print("s1")

                if previous_principle_amount<principle_amount_new:
                    newprincipleamount=principle_amount_new-previous_principle_amount
                    print("newprin")
                    print(newprincipleamount)
                    c.balance=c.balance-newprincipleamount
                    loan2.balance=loan2.balance-newprincipleamount
                    for i in loan_trans:
                        print(i.balance)
                    
                        i.balance=i.balance-newprincipleamount
                        i.save()
                        print(i.balance)
                        print("s3")
                if previous_principle_amount>principle_amount_new:
                    newprincipleamount=previous_principle_amount-principle_amount_new
                    print("newprin")
                    print(newprincipleamount)
                    loan2.balance=loan2.balance+newprincipleamount
                    c.balance=c.balance+newprincipleamount
                    for i in loan_trans:
                        print(i.balance)
                    
                        i.balance=i.balance+newprincipleamount
                        i.save()
                        print(i.balance)
                        print("s3")
            




                loan1.principle_amount=request.POST.get("principal",None)
                loan1.interest_amount=request.POST.get("interest",None)
                loan1.payment_date=request.POST.get("date",None)
                loan1.total_amount=request.POST.get("total",None)
                loan1.principle_amount=request.POST.get("principal",None)

                loan1.payment_method=request.POST.get("select_payment",None)
                loan1.cheque_number=request.POST.get("cheque_no",None)
                loan1.upi_id=request.POST.get("upi_id",None)
                loan1.bank_account=request.POST.get("acc_no",None)
                loan2.save()
                loan1.save()
                c.save()
                trans2 = Fin_Employee_Loan_Transactions_History(company =com ,login_details=login,repayment=loan1,date = date.today(),transaction=c,action='Edited')
                trans2.save()

                return redirect('emploanoverview',loan2.id)
            return render(request, 'company/Employee_loan_repayment_edit.html',context)


def emploanaddtional(request,pk):
    sid = request.session['s_id']
    login = Fin_Login_Details.objects.get(id=sid)
    
    if login.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        loan = Fin_Loan.objects.get(id=pk)
        employee = Employee.objects.get(id=loan.employee.id)
        trans=Fin_Employee_Loan_Transactions.objects.filter(employee_loan=loan)
        banks=Fin_Banking.objects.filter(company=com)
      
        
    elif login.User_Type == 'Staff' :
        staf = Fin_Staff_Details.objects.get(Login_Id = sid)
        com=staf.company_id
        allmodules = Fin_Modules_List.objects.get(company_id = staf.company_id_id)
        loan = Fin_Loan.objects.get(id=pk)
        employee = Employee.objects.filter(company_id=staf.company_id_id)
        trans=Fin_Employee_Loan_Transactions.objects.filter(employee_loan=loan)
        banks=Fin_Banking.objects.filter(company=com)
      

    return render(request,'company/Employee_loan_addtional.html',{'allmodules':allmodules,'loan':loan,'employee':employee,'trans':trans,'com':com,'banks':banks})    



def emploanadditionalsave(request,pk):
    sid = request.session['s_id']
    employee = Fin_Login_Details.objects.get(id=sid)

    if request.method == 'POST':


        balance_loan = request.POST['remain_loan']
        new_loan= request.POST['new']
        total_loan = request.POST['amount']
        payment_date= request.POST['adjdate']
        payment_method = request.POST['select_payment']
        
        cheque_number = request.POST['cheque_no']
        upi_id = request.POST['upi_id']
        bank_account= request.POST['acc_no']
        
        
        
    
        
        sid = request.session['s_id']
        employee = Fin_Login_Details.objects.get(id=sid)
        
        # Assuming principle_amount is a string, convert it to an integer
      

        # Update the loan balance and save
        

        if employee.User_Type == 'Company':
                companykey =  Fin_Company_Details.objects.get(Login_Id_id=sid)
                loan=Fin_Loan.objects.get(id=pk)
                loan.balance=total_loan

                # tt=loan.total_loan
               
                # loan.total_loan= int(new_loan)
                emp=Employee.objects.get(id=loan.employee.id)

                #transaction count 

                loan.transaction_count=loan.transaction_count+1

                # loan.balance=total_loan
                # print(loan.balance)
                # loan_amount=int(loan.total_loan)
                # print(loan_amount)
                # new=int(new_loan)
                # print(new)
                # loan.total_loan=loan_amount+new
                # print(loan.total_loan)
                loan.save()
                        

                new = Fin_Employee_Additional_Loan(company=companykey,login_details=employee,
                                            payment_method=payment_method,total_loan=total_loan,cheque_number=cheque_number,upi_id=upi_id,
                                              bank_account=bank_account,employee_loan=loan,new_loan=new_loan,balance_loan=balance_loan,new_date=payment_date
                                              )
                new.save()
                

                com = Fin_Employee_Additional_Loan.objects.get(id=new.id)
                trans = Fin_Employee_Loan_Transactions(company = companykey,login_details=employee,employee_loan =loan,date = payment_date,particulars = 'ADDITIONAL LOAN',employee=emp,additional=com,balance=total_loan)
                trans.save()
                t = Fin_Employee_Loan_Transactions.objects.get(id=trans.id)
                trans2 = Fin_Employee_Loan_Transactions_History(company =companykey ,login_details=employee,additional =com,date = payment_date,transaction=t,action='Created')
                trans2.save()
        
        elif employee.User_Type == 'Staff':
                staf = Fin_Staff_Details.objects.get(Login_Id = sid)
                loan=Fin_Loan.objects.get(id=pk)
                emp=Employee.objects.get(id=loan.employee.id)

                loan.balance=total_loan
                print(loan.balance)
                loan_amount=int(loan.total_loan)
                print(loan_amount)
                new=int(new_loan)
                print(new)
                loan.total_loan=loan_amount+new
                print(loan.total_loan)

                #transaction count 

                loan.transaction_count=loan.transaction_count+1
                loan.save()
                

                new = Fin_Employee_Additional_Loan(company=staf.company_id,login_details=employee,
                                              payment_method=payment_method,total_loan=total_loan,cheque_number=cheque_number,upi_id=upi_id,
                                              bank_account=bank_account,employee_loan=loan,new_loan=new_loan,balance_loan=balance_loan,new_date=payment_date
                                              )
                new.save()

                com = Fin_Employee_Additional_Loan.objects.get(id=new.id)
                trans = Fin_Employee_Loan_Transactions(company = staf.company_id,login_details=employee,employee_loan =loan,date = payment_date,particulars = 'ADDITIONAL LOAN',employee=emp,additional=com,balance=total_loan)
                trans.save()
                t = Fin_Employee_Loan_Transactions.objects.get(id=trans.id)
                trans2 = Fin_Employee_Loan_Transactions_History(company =staf.company_id ,login_details=employee,additional =com,date = payment_date,transaction=t,action='Created')
                trans2.save()

   
        return redirect(emploanoverview,pk)


def emploanadditionedit(request, pk):                                                                #new by tinto mt
  
    sid = request.session['s_id']
    login = Fin_Login_Details.objects.get(id=sid)

    
    # Retrieve the chart of accounts entry
    # loan = get_object_or_404(Loan, id=pk)
    

    # Check if 'company_id' is in the session

   
    if login.User_Type == 'Company':
      
     
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com.id)
        
        loan_ad = Fin_Employee_Additional_Loan.objects.get(id=pk)
        loan = Fin_Loan.objects.get(id=loan_ad.employee_loan.id)
        banks=Fin_Banking.objects.filter(company=com)
        # employee = Employee.objects.get(id=loan_ad.employee.id)
        context = {
                    'allmodules':allmodules,
                    'loan':loan,
                    # 'employee':employee,
                    'loan_ad':loan_ad,
                    'com':com,
                    'banks':banks
            }
       
    
        
        if request.method=='POST':
        
    
     
            loan1 = Fin_Employee_Additional_Loan.objects.get(id=pk)
            c=Fin_Employee_Loan_Transactions.objects.get(additional=loan1)
            # t=Fin_Employee_Loan_Transactions_History()

            # t.company=com
            # t.login_details=login
            # t.action="Edited"
            # t.date=date.today()
            # t.transaction=c
            # t.additional=loan1
      

            # t.save()
   
       
            loan1.login_details=login
            loan1.company=com
            loan1.employee_loan=loan
            new_loan_amount=request.POST.get("new",None)
            new_loan_amount=int(new_loan_amount)
        # Assuming principle_amount is a string, convert it to an integer
            prevbalance=loan1.balance_loan
            print(prevbalance)
            # Assuming prevbalance, loan1.total_amount, and loan1.interest_amount are strings
            prevbalance = int(prevbalance)
        
            print(prevbalance)
        
            prevnewloan=loan1.new_loan
            prevnewloan=int(prevnewloan)
            previousbalance=c.balance
            previousbalance=int(previousbalance)
            loan_trans = Fin_Employee_Loan_Transactions.objects.filter(Q(employee_loan=c.employee_loan) & Q(id__gte=c.id))
            print("s")
            for i in loan_trans:
                print(i.balance)
                print("s1")

            if prevnewloan<new_loan_amount:
                extraloan=new_loan_amount-prevnewloan
                loan3 = Fin_Loan.objects.get(id=loan_ad.employee_loan.id)
                a=loan3.balance
                print(a)
                d=a+extraloan
                print(d)
                loan3.balance=d
      
                loan3.save()
                e=loan3.balance
                print(e)
                print("extraloan")
                print(extraloan)
                c.balance=c.balance+extraloan
                for i in loan_trans:
                    print(i.balance)
                  
                    i.balance=i.balance+extraloan
                    i.save()
                    print(i.balance)
                    print("s3")
            if prevnewloan>new_loan_amount:
                lessloan=prevnewloan-new_loan_amount
                loan3 = Fin_Loan.objects.get(id=loan_ad.employee_loan.id)
                a=loan3.balance
                print(a)
                d=a-lessloan
                print(d)
                loan3.balance=d
      
                loan3.save()
                e=loan3.balance
                print(e)
             
             
                c.balance=c.balance-lessloan
                for i in loan_trans:
                    print(i.balance)
                  
                    i.balance=i.balance-lessloan
                    i.save()
                    print(i.balance)
                    print("s3")




            loan1.balance_loan=request.POST.get("remain_loan",None)
            loan1.new_loan=request.POST.get("new",None)
            loan1.total_loan=request.POST.get("amount",None)
            loan1.payment_method=request.POST.get("select_payment",None)
           

            loan1.new_date=request.POST.get("adjdate",None)
            loan1.cheque_number=request.POST.get("cheque_no",None)
            loan1.upi_id=request.POST.get("upi_id",None)
            loan1.bank_account=request.POST.get("acc_no",None)
            loan3 = Fin_Loan.objects.get(id=loan_ad.employee_loan.id)
            loan3.save()
            

            loan1.save()
            c.save()
            trans2 = Fin_Employee_Loan_Transactions_History(company =com ,login_details=login,additional=loan1,date = date.today(),transaction=c,action='Edited')
            trans2.save()
            
            # loan2.save()
        
            return redirect('emploanoverview',loan3.id)
        return render(request, 'company/Employee_loan_additional_edit.html',context)
    if login.User_Type == 'Staff':

        staf = Fin_Staff_Details.objects.get(Login_Id = sid)
        com=staf.company_id
        allmodules = Fin_Modules_List.objects.get(company_id = staf.company_id)
        
        loan_ad = Fin_Employee_Additional_Loan.objects.get(id=pk)
        loan = Fin_Loan.objects.get(id=loan_ad.employee_loan.id)
        banks=Fin_Banking.objects.filter(company=com)
        # employee = Employee.objects.get(id=loan_ad.employee.id)
        context = {
                    'allmodules':allmodules,
                    'loan':loan,
                    # 'employee':employee,
                    'loan_ad':loan_ad,
                    'com':com,
                    'banks':banks
            }
       
    
        
        if request.method=='POST':
        
    
     
            loan1 = Fin_Employee_Additional_Loan.objects.get(id=pk)
            c=Fin_Employee_Loan_Transactions.objects.get(additional=loan1)
            # t=Fin_Employee_Loan_Transactions_History()

            # t.company=com
            # t.login_details=login
            # t.action="Edited"
            # t.date=date.today()
            # t.transaction=c
            # t.additional=loan1
      

            # t.save()
   
       
            loan1.login_details=login
            loan1.company=com
            loan1.employee_loan=loan
            new_loan_amount=request.POST.get("new",None)
            new_loan_amount=int(new_loan_amount)
        # Assuming principle_amount is a string, convert it to an integer
            prevbalance=loan1.balance_loan
            print(prevbalance)
            # Assuming prevbalance, loan1.total_amount, and loan1.interest_amount are strings
            prevbalance = int(prevbalance)
        
            print(prevbalance)
        
            prevnewloan=loan1.new_loan
            prevnewloan=int(prevnewloan)
            previousbalance=c.balance
            previousbalance=int(previousbalance)
            loan_trans = Fin_Employee_Loan_Transactions.objects.filter(Q(employee_loan=c.employee_loan) & Q(id__gte=c.id))
            print("s")
            for i in loan_trans:
                print(i.balance)
                print("s1")

            if prevnewloan<new_loan_amount:
                extraloan=new_loan_amount-prevnewloan
                loan3 = Fin_Loan.objects.get(id=loan_ad.employee_loan.id)
                a=loan3.balance
                print(a)
                d=a+extraloan
                print(d)
                loan3.balance=d
      
                loan3.save()
                e=loan3.balance
                print(e)
                print("extraloan")
                print(extraloan)
                c.balance=c.balance+extraloan
                for i in loan_trans:
                    print(i.balance)
                  
                    i.balance=i.balance+extraloan
                    i.save()
                    print(i.balance)
                    print("s3")
            if prevnewloan>new_loan_amount:
                lessloan=prevnewloan-new_loan_amount
                loan3 = Fin_Loan.objects.get(id=loan_ad.employee_loan.id)
                a=loan3.balance
                print(a)
                d=a-lessloan
                print(d)
                loan3.balance=d
      
                loan3.save()
                e=loan3.balance
                print(e)
                print("extraloan")
                print(extraloan)
                c.balance=c.balance-lessloan
                for i in loan_trans:
                    print(i.balance)
                  
                    i.balance=i.balance-lessloan
                    i.save()
                    print(i.balance)
                    print("s3")




            loan1.balance_loan=request.POST.get("remain_loan",None)
            loan1.new_loan=request.POST.get("new",None)
            loan1.total_loan=request.POST.get("amount",None)
            loan1.payment_method=request.POST.get("select_payment",None)
           

            loan1.new_date=request.POST.get("adjdate",None)
            loan1.cheque_number=request.POST.get("cheque_no",None)
            loan1.upi_id=request.POST.get("upi_id",None)
            loan1.bank_account=request.POST.get("acc_no",None)
            loan3 = Fin_Loan.objects.get(id=loan_ad.employee_loan.id)
            loan3.save()
            

            loan1.save()
            c.save()
            trans2 = Fin_Employee_Loan_Transactions_History(company =staf.company_id ,login_details=login,additional=loan1,date = date.today(),transaction=c,action='Edited')
            trans2.save()
        
            return redirect('emploanoverview',loan3.id)
        return render(request, 'company/Employee_loan_additional_edit.html',context)


def addemp(request):                                                                #new by tinto mt (item)
    sid = request.session['s_id']
    login = Fin_Login_Details.objects.get(id=sid)

    
    # Retrieve the chart of accounts entry
    # loan = get_object_or_404(Loan, id=pk)
    

    # Check if 'company_id' is in the session

   
    if login.User_Type == 'Company':
        if request.method == 'POST':
                com = Fin_Company_Details.objects.get(Login_Id = sid)
                allmodules = Fin_Modules_List.objects.get(company_id = com.id)
                title = request.POST['Title']
                firstname = request.POST['First_Name'].capitalize()
                lastname = request.POST['Last_Name'].capitalize()
                # alias = request.POST['Alias']
                joiningdate = request.POST['Joining_Date']
                salarydate = request.POST['Salary_Date']
                salaryamount = request.POST['Salary_Amount']

                if request.POST['Salary_Amount'] == '':
                    salaryamount = None
                else:
                    salaryamount = request.POST['Salary_Amount']

                amountperhour = request.POST['perhour']
                if amountperhour == '' or amountperhour == '0':
                    amountperhour = 0
                else:
                    amountperhour = request.POST['perhour']

                workinghour = request.POST['workhour']
                if workinghour == '' or workinghour == '0':
                    workinghour = 0
                else:
                    workinghour = request.POST['workhour']

                salary_type = request.POST['Salary_Type']
                
                
                employeenumber = request.POST['Employee_Number']
                designation = request.POST['Designation']
                location = request.POST['Location']
                gender = request.POST['Gender']
                image = request.FILES.get('Image', None)
                if image:
                    image = request.FILES['Image']
                else:
                    if gender == 'Male':
                        image = 'media/male_default.png'
                    elif gender == 'Female':
                        image = 'media/female_default.png'
                    else:
                        image = 'media/male_default.png'

                dob = request.POST['DOB']
                blood = request.POST['Blood']
                parent = request.POST['Parent'].capitalize()
                spouse = request.POST['Spouse'].capitalize()
                street = request.POST['street']
                city = request.POST['city']
                state = request.POST['state']
                pincode = request.POST['pincode']
                country = request.POST['country']
                # tempStreet = request.POST['tempStreet']
                # tempCity = request.POST['tempCity']
                # tempState = request.POST['tempState']
                # tempPincode = request.POST['tempPincode']
                # tempCountry = request.POST['tempCountry']
                
                contact = request.POST['Contact_Number']
                emergencycontact = request.POST['Emergency_Contact']
                email = request.POST['Email']
                # file = request.FILES.get('File', None)
                # if file:
                #     file = request.FILES['File']
                # else:
                #     file=''
                bankdetails = request.POST['Bank_Details']
                accoutnumber = request.POST['Account_Number']
                ifsc = request.POST['IFSC']
                bankname = request.POST['BankName']
                branchname = request.POST['BranchName']
                transactiontype = request.POST['Transaction_Type']

                

                if request.POST['tds_applicable'] == 'Yes':
                    tdsapplicable = request.POST['tds_applicable']
                    tdstype = request.POST['TDS_Type']
                    
                    if tdstype == 'Amount':
                        tdsvalue = request.POST['TDS_Amount']
                    elif tdstype == 'Percentage':
                        tdsvalue = request.POST['TDS_Percentage']
                    else:
                        tdsvalue = 0
                elif request.POST['tds_applicable'] == 'No':
                    tdsvalue = 0
                    tdstype = ''
                    tdsapplicable = request.POST['tds_applicable']
                else:
                    tdsvalue = 0
                    tdstype = ''
                    tdsapplicable = ''

                
                
                incometax = request.POST['Income_Tax']
                # aadhar = request.POST['Aadhar']
                uan = request.POST['UAN']
                pf = request.POST['PF']
                pan = request.POST['PAN']
                pr = request.POST['PR']

                if dob == '':
                    age = 2
                else:
                    dob2 = date.fromisoformat(dob)
                    today = date.today()
                    age = int(today.year - dob2.year - ((today.month, today.day) < (dob2.month, dob2.day)))
                


                # if Employee.objects.filter(employee_mail=email,mobile = contact,employee_number=employeenumber,company_id = com.id).exists():
                #     messages.error(request,'user exist')
                #     print('user')
                #     return JsonResponse({"message": "user exist"})
                #     return redirect('employee_loan_create_page')
                
                if Employee.objects.filter(mobile = contact,company_id = com.id).exists():
                    messages.error(request,'phone number exist')
                    print('phone')
                    return JsonResponse({"message": "phone number exist"})

                    return redirect('employee_loan_create_page')
                
                elif Employee.objects.filter(employee_mail=email,company_id = com.id).exists():
                    messages.error(request,'email exist')
                    print('email')
                    return redirect('employee_loan_create_page')
                
                elif Employee.objects.filter(employee_number=employeenumber,company_id = com.id).exists():
                    messages.error(request,'employee id exist')
                    print('id')
                    return JsonResponse({"message": "employee id exist"})

                    return redirect('employee_loan_create_page')
                
                # if Employee.objects.filter(first_name=firstname, company=com).exists():
                #     return JsonResponse({"message": "error"})
                # else:
                    
                # if Employee.objects.filter(employeenumber=employeenumber,company=com,employee_mail=email).exists():
                #         messages.error(request,'Already a Employee  exsits with this details !!!')
                #         return redirect('employee_loan_create_page')
                else:
                    new = Employee(first_name = firstname,last_name = lastname,upload_image=image,title = title,date_of_joining = joiningdate,gender = gender ,
                                        amount_per_hour = amountperhour ,total_working_hours = workinghour,salary_amount = salaryamount ,employee_salary_type =salary_type,salary_effective_from=salarydate,
                                        employee_mail = email,
                                        employee_number = employeenumber,employee_designation = designation,
                                        employee_current_location = location,
                                        mobile = contact,
                                        # temporary_street=tempStreet,temporary_state=tempState,temporary_pincode=tempPincode,temporary_country=tempCountry,
                                        city=city,street=street,state=state,country=country,pincode=pincode,
                                        # temporary_city=tempCity,
                                        employee_status = 'Active' ,company_id = com.id,login_id=sid,date_of_birth = dob ,
                                        age = age,
                                        blood_group = blood,
                                        fathers_name_mothers_name = parent,spouse_name = spouse,
                                        emergency_contact = emergencycontact,
                                        provide_bank_details = bankdetails,account_number = accoutnumber,
                                        ifsc = ifsc,name_of_bank = bankname,branch_name = branchname,bank_transaction_type = transactiontype,
                                        tds_applicable = tdsapplicable, tds_type = tdstype,percentage_amount = tdsvalue,
                                        pan_number = pan,
                                        income_tax_number = incometax,
                                        # aadhar_number = aadhar,
                                        universal_account_number = uan,pf_account_number = pf,
                                        pr_account_number = pr,
                                        # upload_file = file
                                        
                                    )
                                    #   
                                #
                        
                    new.save()

                    history = Employee_History(company_id = com.id,login_id=sid,employee_id = new.id,date = date.today(),action = 'Created')
                    history.save()
                    return JsonResponse({"message": "success"})

    elif login.User_Type == 'Staff':
       
          
        if request.method == 'POST':
                staf = Fin_Staff_Details.objects.get(Login_Id = sid)
                allmodules = Fin_Modules_List.objects.get(company_id = staf.company_id.id)
                title = request.POST['Title']
                firstname = request.POST['First_Name'].capitalize()
                lastname = request.POST['Last_Name'].capitalize()
                # alias = request.POST['Alias']
                joiningdate = request.POST['Joining_Date']
                salarydate = request.POST['Salary_Date']
                salaryamount = request.POST['Salary_Amount']

                if request.POST['Salary_Amount'] == '':
                    salaryamount = None
                else:
                    salaryamount = request.POST['Salary_Amount']

                amountperhour = request.POST['perhour']
                if amountperhour == '' or amountperhour == '0':
                    amountperhour = 0
                else:
                    amountperhour = request.POST['perhour']

                workinghour = request.POST['workhour']
                if workinghour == '' or workinghour == '0':
                    workinghour = 0
                else:
                    workinghour = request.POST['workhour']

                salary_type = request.POST['Salary_Type']

                
                employeenumber = request.POST['Employee_Number']
                designation = request.POST['Designation']
                location = request.POST['Location']
                gender = request.POST['Gender']
                image = request.FILES.get('Image', None)
                if image:
                    image = request.FILES['Image']
                else:
                    if gender == 'Male':
                        image = 'media/male_default.png'
                    elif gender == 'Female':
                        image = 'media/female_default.png'
                    else:
                        image = 'media/male_default.png'

                dob = request.POST['DOB']
                blood = request.POST['Blood']
                parent = request.POST['Parent'].capitalize()
                spouse = request.POST['Spouse'].capitalize()
                street = request.POST['street']
                city = request.POST['city']
                state = request.POST['state']
                pincode = request.POST['pincode']
                country = request.POST['country']
                # tempStreet = request.POST['tempStreet']
                # tempCity = request.POST['tempCity']
                # tempState = request.POST['tempState']
                # tempPincode = request.POST['tempPincode']
                # tempCountry = request.POST['tempCountry']
                
                contact = request.POST['Contact_Number']
                emergencycontact = request.POST['Emergency_Contact']
                email = request.POST['Email']
                # file = request.FILES.get('File', None)
                # if file:
                #     file = request.FILES['File']
                # else:
                #     file=''
                bankdetails = request.POST['Bank_Details']
                accoutnumber = request.POST['Account_Number']
                ifsc = request.POST['IFSC']
                bankname = request.POST['BankName']
                branchname = request.POST['BranchName']
                transactiontype = request.POST['Transaction_Type']

                

                if request.POST['tds_applicable'] == 'Yes':
                    tdsapplicable = request.POST['tds_applicable']
                    tdstype = request.POST['TDS_Type']
                    
                    if tdstype == 'Amount':
                        tdsvalue = request.POST['TDS_Amount']
                    elif tdstype == 'Percentage':
                        tdsvalue = request.POST['TDS_Percentage']
                    else:
                        tdsvalue = 0
                elif request.POST['tds_applicable'] == 'No':
                    tdsvalue = 0
                    tdstype = ''
                    tdsapplicable = request.POST['tds_applicable']
                else:
                    tdsvalue = 0
                    tdstype = ''
                    tdsapplicable = ''

                
                
                incometax = request.POST['Income_Tax']
                # aadhar = request.POST['Aadhar']
                uan = request.POST['UAN']
                pf = request.POST['PF']
                pan = request.POST['PAN']
                pr = request.POST['PR']

                if dob == '':
                    age = 2
                else:
                    dob2 = date.fromisoformat(dob)
                    today = date.today()
                    age = int(today.year - dob2.year - ((today.month, today.day) < (dob2.month, dob2.day)))
                


                # if Employee.objects.filter(employee_mail=email,mobile = contact,employee_number=employeenumber,company_id = staf.company_id.id).exists():
                #     messages.error(request,'user exist')
                #     print('user')
                #     return JsonResponse({"message": "user exist"})
                #     return redirect('employee_loan_create_page')
                
                if Employee.objects.filter(mobile = contact,company_id = staf.company_id.id).exists():
                    messages.error(request,'phone number exist')
                    print('phone')
                    return JsonResponse({"message": "phone number exist"})

                    return redirect('employee_loan_create_page')
                
                elif Employee.objects.filter(employee_mail=email,company_id = staf.company_id.id).exists():
                    messages.error(request,'email exist')
                    print('email')
                    return redirect('employee_loan_create_page')
                
                elif Employee.objects.filter(employee_number=employeenumber,company_id = staf.company_id.id).exists():
                    messages.error(request,'employee id exist')
                    print('id')
                    return JsonResponse({"message": "employee id exist"})

                    return redirect('employee_loan_create_page')
                
                # if Employee.objects.filter(first_name=firstname, company=com).exists():
                #     return JsonResponse({"message": "error"})
                # else:
                    
                # if Employee.objects.filter(employeenumber=employeenumber,company=com,employee_mail=email).exists():
                #         messages.error(request,'Already a Employee  exsits with this details !!!')
                #         return redirect('employee_loan_create_page')
                else:
                    new = Employee(first_name = firstname,last_name = lastname,upload_image=image,title = title,date_of_joining = joiningdate,gender = gender ,
                                        amount_per_hour = amountperhour ,total_working_hours = workinghour,salary_amount = salaryamount ,employee_salary_type =salary_type,salary_effective_from=salarydate,
                                        employee_mail = email,
                                        employee_number = employeenumber,employee_designation = designation,
                                        employee_current_location = location,
                                        mobile = contact,
                                        # temporary_street=tempStreet,temporary_state=tempState,temporary_pincode=tempPincode,temporary_country=tempCountry,
                                        city=city,street=street,state=state,country=country,pincode=pincode,
                                        # temporary_city=tempCity,
                                        employee_status = 'Active' ,company_id = staf.company_id.id,login_id=sid,date_of_birth = dob ,
                                        age = age,
                                        blood_group = blood,
                                        fathers_name_mothers_name = parent,spouse_name = spouse,
                                        emergency_contact = emergencycontact,
                                        provide_bank_details = bankdetails,account_number = accoutnumber,
                                        ifsc = ifsc,name_of_bank = bankname,branch_name = branchname,bank_transaction_type = transactiontype,
                                        tds_applicable = tdsapplicable, tds_type = tdstype,percentage_amount = tdsvalue,
                                        pan_number = pan,
                                        income_tax_number = incometax,
                                        # aadhar_number = aadhar,
                                        universal_account_number = uan,pf_account_number = pf,
                                        pr_account_number = pr,
                                        # upload_file = file
                                        
                                    )
                                    #   
                                #
                        
                    new.save()

                    history = Employee_History(company_id = staf.company_id.id,login_id=sid,employee_id = new.id,date = date.today(),action = 'Created')
                    history.save()
                    return JsonResponse({"message": "success"})

 
def add_term(request):                                                                #new by tinto mt (item)
    sid = request.session['s_id']
    login = Fin_Login_Details.objects.get(id=sid)

    if login.User_Type == 'Company':
        if request.method == 'POST':
            com = Fin_Company_Details.objects.get(Login_Id = sid)
            allmodules = Fin_Modules_List.objects.get(company_id = com.id)
            duration = request.POST['duration']
            term = request.POST['term']
            if term=="YEAR":
                days= int(duration) * 365
            else:
                days=int(duration)*30
           
            
            if Fin_Loan_Term.objects.filter(duration=duration, company=com,term=term).exists():
                return JsonResponse({"message": "error"})
            else:
                term = Fin_Loan_Term(duration=duration, company=com,term=term,days=days)  
                term.save()  
                return JsonResponse({"message": "success"})
    elif login.User_Type == 'Staff':
        if request.method == 'POST':
            staf = Fin_Staff_Details.objects.get(Login_Id = sid)
            allmodules = Fin_Modules_List.objects.get(company_id = staf.company_id)
            duration = request.POST['duration']
            term = request.POST['term']
            if term=="YEAR":
                days= int(duration) * 365
            else:
                days=int(duration)*30
           
            
            if Fin_Loan_Term.objects.filter(duration=duration, company=staf.company_id,term=term).exists():
                return JsonResponse({"message": "error"})
            else:
                term = Fin_Loan_Term(duration=duration, company=staf.company_id,term=term,days=days)  
                term.save()  
                return JsonResponse({"message": "success"})
                
def term_dropdown(request):                                                                 #new by tinto mt (item)
    sid = request.session['s_id']
    login = Fin_Login_Details.objects.get(id=sid)
    if login.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = sid)
            options = {}
            option_objects = Fin_Loan_Term.objects.filter(company=com)
            for option in option_objects:
                duration=option.duration
                term=option.term
                options[option.id] = [duration,term,f"{duration}"]
            return JsonResponse(options)
    elif login.User_Type == 'Staff':
            staf = Fin_Staff_Details.objects.get(Login_Id = sid)
            options = {}
            option_objects =Fin_Loan_Term.objects.filter(company=staf.company_id)
            for option in option_objects:
                duration=option.duration
                term=option.term
                options[option.id] = [duration,term,f"{duration}"]
            return JsonResponse(options)
    
def emp_dropdown(request):                                                                 #new by tinto mt (item)
    sid = request.session['s_id']
    login = Fin_Login_Details.objects.get(id=sid)
    if login.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = sid)
            options = {}
            option_objects = Employee.objects.filter(company=com,employee_status='Active')
            print(1111)
            for option in option_objects:
                title=option.title
                first_name=option.first_name
                last_name=option.last_name
                options[option.id] = [title,first_name,last_name,f"{title}"]
            return JsonResponse(options)
    elif login.User_Type == 'Staff':
            staf = Fin_Staff_Details.objects.get(Login_Id = sid)
            options = {}
            option_objects = Employee.objects.filter(company=staf.company_id,employee_status='Active')
            for option in option_objects:
                title=option.title
                first_name=option.first_name
                last_name=option.last_name
                options[option.id] = [title,first_name,last_name,f"{title}"]
            return JsonResponse(options)
    

def laon_status_edit(request, pk):                                                                #new by tinto mt
    
    loan = Fin_Loan.objects.get(id=pk)

    if loan.status == 'Active':
        loan.status = 'Inactive'
        loan.save()
    elif loan.status != 'Active':
        loan.status = 'Active'
        loan.save()

    loan.save()

    return redirect('emploanoverview',pk)


def add_loan_comment(request,pk):
    sid = request.session['s_id']
    login = Fin_Login_Details.objects.get(id=sid)
    
    if login.User_Type == 'Company':
        com1 = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com1.id)
        loan = Fin_Loan.objects.get(id=pk)
        if request.method=="POST":
                    
                    com=Fin_Employee_loan_comments()
                    
            
                    comment_comments=request.POST['comment']
                    com.company=com1
                    com.logindetails=login
                    com.comments=comment_comments
                    acc=Fin_Loan.objects.get(id=pk)
                    com.employee_loan=acc
                    
                    com.save()
                    return redirect('emploanoverview',pk)
      
        
    elif login.User_Type == 'Staff' :
        staf = Fin_Staff_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = staf.company_id_id)
        if request.method=="POST":
                    
                    com=Fin_Employee_loan_comments()
                    
            
                    comment_comments=request.POST['comment']
                    com.company=staf.company_id
                    com.logindetails=login
                    com.comments=comment_comments
                    acc=Fin_Loan.objects.get(id=pk)
                    com.employee_loan=acc
                    
                    com.save()
                    return redirect('emploanoverview',pk)
        

def delete_loan_comment(request,ph,pr):                                                                #new by tinto mt
    acc=Fin_Employee_loan_comments.objects.get(id=ph)
    acc.delete()
    ac=Fin_Loan.objects.get(id=pr)
    
    return redirect(emploanoverview,ac.id)

def attach_loan_file(request,pk):                       
    estobj= Fin_Loan.objects.get(id=pk)
    if request.method == 'POST':
        if len(request.FILES) != 0:
            estobj.attach_file=request.FILES.get('file')
            estobj.save()
            return redirect('emploanoverview',estobj.id)
    
    return redirect(emploanoverview,pk)
    
def delete_loan(request,pk):                                                                #new by tinto mt
    acc=Fin_Loan.objects.get(id=pk)
    acc.delete()
  
    
    return redirect(employee_loan_list)


def shareloanToEmail(request,pk):   
    sid = request.session['s_id']
    login = Fin_Login_Details.objects.get(id=sid)
    
    if login.User_Type == 'Company':
        com1 = Fin_Company_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = com1.id)
        loan = Fin_Loan.objects.get(id=pk)
        try:
            if request.method == 'POST':
                emails_string = request.POST['email_ids']
                # Split the string by commas and remove any leading or trailing whitespace
                emails_list = [email.strip() for email in emails_string.split(',')]
                email_message = request.POST['email_message']
                fdate = request.POST['fdate_modal']
                ldate = request.POST['ldate_modal']
                print(fdate)
                print(ldate)
                print(emails_list)
                print('1')
           
           
                loan = Fin_Loan.objects.get(id=pk)
                est_comments = Fin_Employee_loan_comments.objects.filter(employee_loan=loan)
                employee = Employee.objects.get(id=loan.employee.id)
                fdate_obj = datetime.strptime(fdate, '%Y-%m-%d')
                ldate_obj = datetime.strptime(ldate, '%Y-%m-%d')

                # Assuming 'transaction_date' is the field in your model representing the transaction date
                trans = Fin_Employee_Loan_Transactions.objects.filter(
                    employee_loan=loan,
                    date__range=(fdate_obj, ldate_obj)
                )
                latest_item_id=Fin_Employee_Loan_History.objects.filter(employee_loan=loan,company=com1)
                context = {
                
                    'loan':loan,
                    'est_comments':est_comments,
                    'employee':employee,
                    'trans':trans,
                    'latest_item_id':latest_item_id


                }
                print('2')
                template_path = 'company/Employee_loan_emailpdf.html'
                print('3')
                template = get_template(template_path)
                print('4')
                html  = template.render(context)
                result = BytesIO()
                pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)#, link_callback=fetch_resources)
                pdf = result.getvalue()
                print('5')
                filename = f'Loan Transactions.pdf'
                subject = f"Transactipns"
                email = EmailMessage(subject, f"Hi,\nPlease find the attached Loan transactions. \n{email_message}\n\n--\nRegards,\n", from_email=settings.EMAIL_HOST_USER,to=emails_list)
                email.attach(filename,pdf,"application/pdf")
                email.send(fail_silently=False)
                msg = messages.success(request, 'Details has been shared via email successfully..!')
                return redirect(emploanoverview,pk)
        except Exception as e:
            print(e)
            messages.error(request, f'{e}')
            return redirect(emploanoverview,pk)   
      
        
    elif login.User_Type == 'Staff' :
        staf = Fin_Staff_Details.objects.get(Login_Id = sid)
        allmodules = Fin_Modules_List.objects.get(company_id = staf.company_id_id)
        loan = Fin_Loan.objects.get(id=pk)
        try:
            if request.method == 'POST':
                emails_string = request.POST['email_ids']
                # Split the string by commas and remove any leading or trailing whitespace
                emails_list = [email.strip() for email in emails_string.split(',')]
                email_message = request.POST['email_message']
                print(emails_list)
                fdate = request.POST['fdate_modal']
                ldate = request.POST['ldate_modal']
                print('1')
           
           
                loan = Fin_Loan.objects.get(id=pk)
                est_comments = Fin_Employee_loan_comments.objects.filter(employee_loan=loan)
                employee = Employee.objects.get(id=loan.employee.id)
                fdate_obj = datetime.strptime(fdate, '%Y-%m-%d')
                ldate_obj = datetime.strptime(ldate, '%Y-%m-%d')

                # Assuming 'transaction_date' is the field in your model representing the transaction date
                trans = Fin_Employee_Loan_Transactions.objects.filter(
                    employee_loan=loan,
                    date__range=(fdate_obj, ldate_obj)
                )
                latest_item_id=Fin_Employee_Loan_History.objects.filter(employee_loan=loan,company=staf.company_id)
                context = {
                
                    'loan':loan,
                    'est_comments':est_comments,
                    'employee':employee,
                    'trans':trans,
                    'latest_item_id':latest_item_id


                }
                print('2')
                template_path = 'company/Employee_loan_emailpdf.html'
                print('3')
                template = get_template(template_path)
                print('4')
                html  = template.render(context)
                result = BytesIO()
                pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)#, link_callback=fetch_resources)
                pdf = result.getvalue()
                print('5')
                filename = f'Loan Transactions.pdf'
                subject = f"Transactipns"
                email = EmailMessage(subject, f"Hi,\nPlease find the attached Loan transactions. \n{email_message}\n\n--\nRegards,\n", from_email=settings.EMAIL_HOST_USER,to=emails_list)
                email.attach(filename,pdf,"application/pdf")
                email.send(fail_silently=False)
                msg = messages.success(request, 'Details has been shared via email successfully..!')
                return redirect(emploanoverview,pk)
        except Exception as e:
            print(e)
            messages.error(request, f'{e}')
            return redirect(emploanoverview,pk)   
      

def bankdata(request):
    sid = request.session['s_id']
    login = Fin_Login_Details.objects.get(id=sid)
    
    if login.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        customer_id = request.GET.get('id')
        cust = Fin_Banking.objects.get(id=customer_id,company_id=com.id)
        data7 = {'acc': cust.account_number,'name':cust.bank_name}
        return JsonResponse(data7)

      
        
    elif login.User_Type == 'Staff' :
        staf = Fin_Staff_Details.objects.get(Login_Id = sid)
        customer_id = request.GET.get('id')
        cust = Fin_Banking.objects.get(id=customer_id,company_id=staf.company_id_id)
        data7 = {'acc': cust.account_number,'name':cust.bank_name}
        return JsonResponse(data7)


def get_repayment_data(request):                                                                 #new by tinto mt (item)
    sid = request.session['s_id']
    login = Fin_Login_Details.objects.get(id=sid)
    if login.User_Type == 'Company':
            id = request.GET.get('repaymentId2')
            print('repay')
            print(id)
            # com = Fin_Company_Details.objects.get(Login_Id = sid)
            options = {}
            option_objects = Fin_Employee_Loan_Transactions_History.objects.filter(transaction=id)
            print(1111)
            # for i in option_objects:
            #     print(i.action)
            #     print("s1")
            for option in option_objects:
                date=option.date
                action=option.action
                print(option.action)
                first_name=option.login_details.First_name
                last_name=option.login_details.Last_name
                options[option.id] = [date,action,first_name,last_name,f"{date}"]
            return JsonResponse(options)
    elif login.User_Type == 'Staff':
            id = request.GET.get('repaymentId2')
            # staf = Fin_Staff_Details.objects.get(Login_Id = sid)
            options = {}
            option_objects = Fin_Employee_Loan_Transactions_History.objects.filter(transaction=id)
            print(1111)
            for option in option_objects:
                date=option.date
                action=option.action
                first_name=option.login_details.First_name
                last_name=option.login_details.Last_name
                options[option.id] = [date,action,first_name,last_name,f"{date}"]
            return JsonResponse(options)
            return JsonResponse(options)
    
def get_addition_data(request):                                                                 #new by tinto mt (item)
    sid = request.session['s_id']
    login = Fin_Login_Details.objects.get(id=sid)
    if login.User_Type == 'Company':
            id = request.GET.get('additionalId2')
            # com = Fin_Company_Details.objects.get(Login_Id = sid)
            options = {}
            option_objects = Fin_Employee_Loan_Transactions_History.objects.filter(transaction=id)
            print(1111)
            for option in option_objects:
                date=option.date
                action=option.action
                first_name=option.login_details.First_name
                last_name=option.login_details.Last_name
                options[option.id] = [date,action,first_name,last_name,f"{date}"]
            return JsonResponse(options)
    elif login.User_Type == 'Staff':
            id = request.GET.get('additionalId2')
            # staf = Fin_Staff_Details.objects.get(Login_Id = sid)
            options = {}
            option_objects = Fin_Employee_Loan_Transactions_History.objects.filter(transaction=id)
            print(1111)
            for option in option_objects:
                date=option.date
                action=option.action
                first_name=option.login_details.First_name
                last_name=option.login_details.Last_name
                options[option.id] = [date,action,first_name,last_name,f"{date}"]
            return JsonResponse(options)


def delete_loan_repayment(request,pk):                                                                #new by tinto mt
    # acc=Fin_Employee_Loan_Repayment.objects.get(id=pk)
    # princ=acc.principle_amount
    c=Fin_Employee_Loan_Transactions.objects.get(id=pk)
    acc=Fin_Employee_Loan_Repayment.objects.get(id=c.repayment.id)

    princ=acc.principle_amount
    loan_trans = Fin_Employee_Loan_Transactions.objects.filter(Q(employee_loan=c.employee_loan) & Q(id__gte=c.id))
    cd=Fin_Loan.objects.get(id=acc.employee_loan.id)

    #transaction count --

    cd.transaction_count=cd.transaction_count-1
    # bal=c.balance
    # print('test')
    # print(bal)
    # cd.balance=bal+princ

    
    print("s")
    for i in loan_trans:
        print(i.balance)
        print("s1")
        c=i.balance+princ
        i.balance=c
        last_balance = i.balance
        i.save()
    if last_balance is not None:
    # Assuming you have an object where you want to save the last balance, let's call it 'loan_object'
        cd.balance = last_balance
        cd.save()

    acc.delete()
  
    
    return redirect(emploanoverview,cd.id)

def delete_loan_additional(request,pk):                                                                #new by tinto mt
    # acc=Fin_Employee_Loan_Repayment.objects.get(id=pk)
    # princ=acc.principle_amount
    c=Fin_Employee_Loan_Transactions.objects.get(id=pk)
    acc=Fin_Employee_Additional_Loan.objects.get(id=c.additional.id)

    loanadded=acc.new_loan
    loan_trans = Fin_Employee_Loan_Transactions.objects.filter(Q(employee_loan=c.employee_loan) & Q(id__gte=c.id))
    cd=Fin_Loan.objects.get(id=c.employee_loan.id)
    #transaction count --

    cd.transaction_count=cd.transaction_count-1
    # bal=c.balance
    # cd.balance=bal-loanadded
    # cd.save()
    print("s")
    for i in loan_trans:
        print(i.balance)
        print("s1")
        c=i.balance-loanadded
        i.balance=c
        last_balance = i.balance
        i.save()
    if last_balance is not None:
    # Assuming you have an object where you want to save the last balance, let's call it 'loan_object'
        cd.balance = last_balance
        cd.save()

    acc.delete()
  
    
    return redirect(emploanoverview,cd.id)
    
#End

# CREATED BY AISWARYA
def Fin_Eway_bills(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        try:
            data = Fin_Login_Details.objects.get(id=s_id)
            if data.User_Type == "Company":
                com = Fin_Company_Details.objects.get(Login_Id=s_id)
                allmodules = Fin_Modules_List.objects.get(Login_Id=s_id,status='New')
                eway_bill = Fin_Ewaybills.objects.filter(Company=com)
            else:
                com = Fin_Staff_Details.objects.get(Login_Id=s_id)
                allmodules = Fin_Modules_List.objects.get(company_id=com.company_id, status='New')
                eway_bill = Fin_Ewaybills.objects.filter(Company_id=com.company_id)
                
            sort_by = request.GET.get('sort_by', None)
            if sort_by == 'customer_name':
                eway_bill = eway_bill.order_by('Customer_Name')
            elif sort_by == 'eway_billnumber':
                eway_bill = eway_bill.order_by('EwayBill_No')

            context = {
                'com': com,
                'sort_by': sort_by,
                'eway_bill':eway_bill,
                'allmodules':allmodules,
                'data':data,              
            }
            return render(request, 'company/Fin_Ewaybills.html', context)
        except Fin_Login_Details.DoesNotExist:
            return redirect('/')
    else:
        return redirect('/')  


def Fin_load_CreateEwaybill(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        try:
            data = Fin_Login_Details.objects.get(id=s_id)
            if data.User_Type == "Company":
                com = Fin_Company_Details.objects.get(Login_Id=data)
                cmp = com
                allmodules = Fin_Modules_List.objects.get(Login_Id=s_id, status='New')
                
            else:
                com = Fin_Staff_Details.objects.get(Login_Id=data)
                cmp = com.company_id
                allmodules = Fin_Modules_List.objects.get(company_id=com.company_id, status='New')
               
            eway_bill = Fin_Ewaybills.objects.filter(Company=cmp)
            cust = Fin_Customers.objects.filter(Company=cmp, status='Active')
            itms = Fin_Items.objects.filter(Company=cmp, status='Active')
            units = Fin_Units.objects.filter(Company=cmp)
            acc = Fin_Chart_Of_Account.objects.filter(Q(account_type='Expense') | Q(account_type='Other Expense') | Q(account_type='Cost Of Goods Sold'), Company=cmp).order_by('account_name')
            lst = Fin_Price_List.objects.filter(Company=cmp, status='Active')
            transportation = Fin_Eway_Transportation.objects.filter(Company=cmp)
            trms = Fin_Company_Payment_Terms.objects.filter(Company = cmp)
            eway_item = Fin_Eway_Items.objects.filter(Company = cmp)
            latest_eway = Fin_Ewaybills.objects.filter(Company=cmp).order_by('-Ewaybill_No').first()

            new_number = int(latest_eway.ReferenceNumber) + 1 if latest_eway else 1

            if Fin_Eway_Reference.objects.filter(Company=cmp).exists():
                deleted = Fin_Eway_Reference.objects.get(Company=cmp)
                
                if deleted:
                    while int(deleted.reference_no) >= new_number:
                        new_number += 1

            nxtEway = ""
            lastEway = Fin_Ewaybills.objects.filter(Company=cmp).last()
            if lastEway:
                eway_no = str(lastEway.Ewaybill_No)
                numbers = []
                stri = []
                for word in eway_no:
                    if word.isdigit():
                        numbers.append(word)
                    else:
                        stri.append(word)

                num = ''.join(numbers)
                st = ''.join(stri)

                eway_num = int(num) + 1

                if num[0] == '0':
                    nxtEway = st + '0' + str(eway_num)
                else:
                    nxtEway = st + str(eway_num)

            context = {
                'com': com,
                'cmp' : cmp,
                'LoginDetails': data,
                'allmodules': allmodules,
                'data': data,
                'eway_bill': eway_bill,
                'customers': cust,
                'items': itms,
                'lst': lst,
                'Transportation': transportation,
                'ref_no':new_number,
                'ewayNo':nxtEway,
                'pTerms':trms,
                'accounts':acc,
                'units':units,
                'eway_item':eway_item,
            }
            return render(request, 'company/Fin_CreateEwaybill.html', context)
        except Fin_Login_Details.DoesNotExist:
            return redirect('/')
    return redirect('Fin_Eway_bills')


def Fin_checkEwayNumber(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id=s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id=s_id).company_id

        ewayNo = request.GET['eway_num']

        nxtEway = ""
        lastEway = Fin_Ewaybills.objects.filter(Company=com).last()

        if lastEway:
            # Extract numeric and non-numeric parts of the last Eway-Bill number
            numbers = ''.join([c for c in str(lastEway.Ewaybill_No) if c.isdigit()])
            non_numbers = ''.join([c for c in str(lastEway.Ewaybill_No) if not c.isdigit()])

            # Calculate the next Eway-Bill number
            eway_num = int(numbers) + 1
            nxtEway = f'{non_numbers}{eway_num:02d}'

        if Fin_Ewaybills.objects.filter(Company=com, Ewaybill_No__iexact=ewayNo).exists():
            return JsonResponse({'status': False, 'message': 'Eway-Bill No already exists!'})
        elif nxtEway and ewayNo != nxtEway:
            return JsonResponse({'status': False, 'message': 'Eway-Bill No is not continuous!'})
        else:
            return JsonResponse({'status': True, 'message': 'Number is okay!'})
    else:
        return redirect('/')
    

def Fin_getEwayItemDetails(request):
    try:
        if 's_id' in request.session:
            s_id = request.session['s_id']
            data = Fin_Login_Details.objects.get(id=s_id)

            if data.User_Type == "Company":
                com = Fin_Company_Details.objects.get(Login_Id=s_id)
            else:
                com = Fin_Staff_Details.objects.get(Login_Id=s_id).company_id
            
            itemName = request.GET.get('item')
            priceListId = request.GET.get('listId')
            item = Fin_Items.objects.get(Company=com, name=itemName)

            if priceListId:
                priceList = Fin_Price_List.objects.get(id=int(priceListId))

                if priceList.item_rate == 'Customized individual rate':
                    try:
                        priceListPrice = float(Fin_PriceList_Items.objects.get(Company=com, list=priceList, item=item).custom_rate)
                    except:
                        priceListPrice = item.selling_price
                else:
                    mark = priceList.up_or_down
                    percentage = float(priceList.percentage)
                    roundOff = priceList.round_off

                    if mark == 'Markup':
                        price = float(item.selling_price) + float((item.selling_price) * (percentage / 100))
                    else:
                        price = float(item.selling_price) - float((item.selling_price) * (percentage / 100))

                    if priceList.round_off != 'Never mind':
                        if roundOff == 'Nearest whole number':
                            finalPrice = round(price)
                        else:
                            finalPrice = int(price) + float(roundOff)
                    else:
                        finalPrice = price

                    priceListPrice = finalPrice
            else:
                priceListPrice = None

            context = {
                'status': True,
                'id': item.id,
                'hsn': item.hsn,
                'sales_rate': item.selling_price,
                'avl': item.current_stock,
                'tax': True if item.tax_reference == 'taxable' else False,
                'gst': item.intra_state_tax,
                'igst': item.inter_state_tax,
                'PLPrice': priceListPrice,
            }
            return JsonResponse(context)
    except Fin_Items.DoesNotExist:
        logging.error('Item not found: %s', itemName)
    except Exception as e:
        logging.error('An error occurred in Fin_getEwayItemDetails: %s', str(e))

    return JsonResponse({'status': False})


def Fin_getEwayCustomerData(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
        
        custId = request.POST['id']
        cust = Fin_Customers.objects.get(id = custId)

        if cust:
            if cust.price_list and cust.price_list.type == 'Sales':
                list = True
                listId = cust.price_list.id
                listName = cust.price_list.name
            else:
                list = False
                listId = None
                listName = None
            context = {
                'status':True, 'id':cust.id, 'email':cust.email, 'gstType':cust.gst_type,'shipState':cust.ship_state,'gstin':False if cust.gstin == "" or cust.gstin == None else True, 'gstNo':cust.gstin, 'priceList':list, 'ListId':listId, 'ListName':listName,
                'street':cust.billing_street, 'city':cust.billing_city, 'state':cust.billing_state, 'country':cust.billing_country, 'pincode':cust.billing_pincode
            }
            return JsonResponse(context)
        else:
            return JsonResponse({'status':False, 'message':'Something went wrong..!'})
    else:
       return redirect('/')


def Fin_createEwayCustomer(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
            lst = Fin_Price_List.objects.filter(Company=com, status='Active')
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
            lst = Fin_Price_List.objects.filter(Company=com.company_id, status='Active')

        fName = request.POST['first_name']
        lName = request.POST['last_name']
        gstIn = request.POST['gstin']
        pan = request.POST['pan_no']
        email = request.POST['email']
        phn = request.POST['mobile']

        if Fin_Customers.objects.filter(Company = com, first_name__iexact = fName, last_name__iexact = lName).exists():
            res = f"Customer `{fName} {lName}` already exists, try another!"
            return JsonResponse({'status': False, 'message':res})
        elif gstIn != "" and Fin_Customers.objects.filter(Company = com, gstin__iexact = gstIn).exists():
            res = f"GSTIN `{gstIn}` already exists, try another!"
            return JsonResponse({'status': False, 'message':res})
        elif Fin_Customers.objects.filter(Company = com, pan_no__iexact = pan).exists():
            res = f"PAN No `{pan}` already exists, try another!"
            return JsonResponse({'status': False, 'message':res})
        elif Fin_Customers.objects.filter(Company = com, mobile__iexact = phn).exists():
            res = f"Phone Number `{phn}` already exists, try another!"
            return JsonResponse({'status': False, 'message':res})
        elif Fin_Customers.objects.filter(Company = com, email__iexact = email).exists():
            res = f"Email `{email}` already exists, try another!"
            return JsonResponse({'status': False, 'message':res})

        cust = Fin_Customers(
            Company = com,
            LoginDetails = data,
            title = request.POST['title'],
            first_name = fName,
            last_name = lName,
            company = request.POST['company_name'],
            location = request.POST['location'],
            place_of_supply = request.POST['place_of_supply'],
            gst_type = request.POST['gst_type'],
            gstin = None if request.POST['gst_type'] == "Unregistered Business" or request.POST['gst_type'] == 'Overseas' or request.POST['gst_type'] == 'Consumer' else gstIn,
            pan_no = pan,
            email = email,
            mobile = phn,
            website = request.POST['website'],
            price_list = None if request.POST['price_list'] ==  "" else Fin_Price_List.objects.get(id = request.POST['price_list']),
            payment_terms = None if request.POST['payment_terms'] == "" else Fin_Company_Payment_Terms.objects.get(id = request.POST['payment_terms']),
            opening_balance = 0 if request.POST['open_balance'] == "" else float(request.POST['open_balance']),
            open_balance_type = request.POST['balance_type'],
            current_balance = 0 if request.POST['open_balance'] == "" else float(request.POST['open_balance']),
            credit_limit = 0 if request.POST['credit_limit'] == "" else float(request.POST['credit_limit']),
            billing_street = request.POST['street'],
            billing_city = request.POST['city'],
            billing_state = request.POST['state'],
            billing_pincode = request.POST['pincode'],
            billing_country = request.POST['country'],
            ship_street = request.POST['shipstreet'],
            ship_city = request.POST['shipcity'],
            ship_state = request.POST['shipstate'],
            ship_pincode = request.POST['shippincode'],
            ship_country = request.POST['shipcountry'],
            status = 'Active'
        )
        cust.save()

        

        Fin_Customers_History.objects.create(
            Company = com,
            LoginDetails = data,
            customer = cust,
            action = 'Created'
        )

        return JsonResponse({'status': True})
    
    else:
        return redirect('/')
    
def Fin_getEwayCustomers(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        options = {}
        option_objects = Fin_Customers.objects.filter(Company = com, status = 'Active')
        for option in option_objects:
            options[option.id] = [option.id , option.title, option.first_name, option.last_name]

        return JsonResponse(options)
    else:
        return redirect('/')


def Fin_createEwayItem(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
            ewaybill = Fin_Ewaybills.objects.filter(Company=com)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
            ewaybill = Fin_Ewaybills.objects.filter(Company=com.company_id)

        name = request.POST['name']
        type = request.POST['type']
        unit = request.POST.get('unit')
        hsn = request.POST['hsn']
        tax = request.POST['taxref']
        gstTax = 0 if tax == 'non taxable' else request.POST['intra_st']
        igstTax = 0 if tax == 'non taxable' else request.POST['inter_st']
        purPrice = request.POST['pcost']
        salePrice = request.POST['salesprice']
        createdDate = date.today()
        
    
        if Fin_Items.objects.filter(Company=com, name__iexact=name).exists():
            res = f"{name} already exists, try another!"
            return JsonResponse({'status': False, 'message':res})
        elif Fin_Items.objects.filter(Company = com, hsn__iexact = hsn).exists():
            res = f"HSN - {hsn} already exists, try another.!"
            return JsonResponse({'status': False, 'message':res})
        else:
            item = Fin_Items(
                Company = com,
                LoginDetails = data,
                name = name,
                item_type = type,
                unit = unit,
                hsn = hsn,
                tax_reference = tax,
                intra_state_tax = gstTax,
                inter_state_tax = igstTax,
                selling_price = salePrice,
                purchase_price = purPrice,
                item_created = createdDate,
                status = 'Active'
            )
            item.save()

            
            Fin_Items_Transaction_History.objects.create(
                Company = com,
                LoginDetails = data,
                item = item,
                action = 'Created'
            )
            
            return JsonResponse({'status': True})
    else:
       return redirect('/')

def Fin_getEwayItems(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        items = {}
        option_objects = Fin_Items.objects.filter(Company = com, status='Active')
        for option in option_objects:
            items[option.id] = [option.name]

        return JsonResponse(items)
    else:
        return redirect('/')


def Fin_new_transport_mode(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id=s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
            
        else:
            com = Fin_Staff_Details.objects.get(Login_Id=s_id).company_id

       

        if request.method == 'POST':
            transport = request.POST['new_transport']
            transport_type = request.POST['transport_type']
            trnsp = Fin_Eway_Transportation(Name=transport, Type=transport_type, Company=com)
            trnsp.save()
            return JsonResponse({"message": "success"})


def Fin_get_transport_data(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id=s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id=s_id).company_id

    if request.method == 'POST':
        trnsp = Fin_Eway_Transportation.objects.get(id=request.POST['id'].split(" ")[0])
        if trnsp.Type == 'Road':
            return JsonResponse({'status': 'true'})
        else:
            return JsonResponse({'status': 'false'})

def Fin_transportation_modes(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id=s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id=s_id).company_id
        
        
        options = {}
        option_objects = Fin_Eway_Transportation.objects.filter(Company=com)
        for option in option_objects:
            options[option.id] = option.Name 

        

        return JsonResponse(options)


from decimal import Decimal
def Fin_CreateEwaybill(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id=s_id)
        
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
            eway_bills = Fin_Ewaybills.objects.filter(Company=com)
            eway_item = Fin_Eway_Items.objects.filter(Company=com)
            allmodules = Fin_Modules_List.objects.get(Login_Id=s_id, status='New')
            
        else:
            staff_details = Fin_Staff_Details.objects.get(Login_Id=s_id)
            com = staff_details.company_id 
            eway_bills = Fin_Ewaybills.objects.filter(Company=com)
            eway_item = Fin_Eway_Items.objects.filter(Company=com)
            allmodules = Fin_Modules_List.objects.get(company_id=com, status='New')
           

        current_date = datetime.now().date()

        if request.method == 'POST':
            ewaybill_num = request.POST['Ewaybill_No']
            deliver_to_different_address = request.POST.get('deliver_to_different_address', '0')

            delivery_name = request.POST.get('delivery_name', '')
            delivery_address = request.POST.get('delivery_address', '')
            delivery_phone = request.POST.get('delivery_phone', '')
            delivery_email = request.POST.get('delivery_email', '')
            delivery_place = request.POST.get('delivery_place_of_supply', '')

            if Fin_Ewaybills.objects.filter(Company=com, Ewaybill_No__iexact=ewaybill_num).exists():
                error_script = f'<script>alert("E-waybill Number `{ewaybill_num}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(error_script)

            File = request.FILES.get('file', None)
            tax_amount_str = request.POST.get('taxamount', '0.0')
            print(f"Debug: tax_amount = {tax_amount_str}, type = {type(tax_amount_str)}")
            tax_amount = Decimal(tax_amount_str)


            if 'transport_mode' not in request.POST:
                alert_script = '<script>alert("Please choose a transportation mode.");</script>'
                return HttpResponse(alert_script + '<script>window.history.back();</script>')

            
            transportation_id = request.POST['transport_mode'].split(" ")[0]

            ewaybill = Fin_Ewaybills(
                Company=com,
                LoginDetails=com.Login_Id,
                Ewaybill_No=ewaybill_num,
                BillDate=request.POST['date'],
                DocumentType=request.POST['document_type'],
                TransactionSubtype=request.POST['transaction_subtype'],
                TransactionType=request.POST['transaction_subtype'],
                Customer=Fin_Customers.objects.get(id=request.POST['customer']),
                CustomerName=request.POST['customer'],
                CustomerEmail=request.POST['customer'],
                Customer_GstType=request.POST['gst_type'],
                Customer_GstNumber=request.POST['gstin'],
                Customer_PlaceOfSupply=request.POST['place_of_supply'],
                BillingAddress=request.POST['bill_address'],
                ReferenceNumber=request.POST['reference_number'],
                Date=request.POST['date'],
                Transportation = Fin_Eway_Transportation.objects.get(id=transportation_id),
                VehicleNumber=request.POST['vehicle_number'],
                Kilometer=request.POST['kilometer'],
                SubTotal=Decimal(request.POST['subtotal']) if request.POST['subtotal'] != "" else Decimal('0.0'), 
                Igst=Decimal(request.POST['igst']) if request.POST['igst'] != "" else Decimal('0.0'),  
                Cgst=Decimal(request.POST['cgst']) if request.POST['cgst'] != "" else Decimal('0.0'),  
                Sgst=Decimal(request.POST['sgst']) if request.POST['sgst'] != "" else Decimal('0.0'),  
                TaxAmount=tax_amount,
                ShippingCharge=Decimal(request.POST['ship']) if request.POST['ship'] != "" else Decimal('0.0'),  
                Adjustment=Decimal(request.POST['adj']) if request.POST['adj'] != "" else Decimal('0.0'), 
                GrandTotal=Decimal(request.POST['grandtotal']) if request.POST['grandtotal'] != "" else Decimal('0.0'),  
                Note=request.POST['note'],
                File=File,
                Status=request.POST.get('Saved', 'Draft')
            )
            ewaybill.save()
            
            if deliver_to_different_address == '1':
                ewaybill.DeliverToDifferentAddress = True
                ewaybill.DeliveryName = delivery_name
                ewaybill.DeliveryAddress = delivery_address
                ewaybill.DeliveryPhone = delivery_phone
                ewaybill.DeliveryEmail = delivery_email
                ewaybill.DeliveryPlace = delivery_place
                ewaybill.save()

            if 'Draft' in request.POST:
                ewaybill.Status = "Draft"
            elif 'Save' in request.POST:
                ewaybill.Status = "Saved"
      
            ewaybill.save()

            itemId = request.POST.getlist("item_id[]")
            itemName = request.POST.getlist("item_name[]")
            hsn = request.POST.getlist("hsn[]")
            qty = request.POST.getlist("qty[]")
            price = request.POST.getlist("priceListPrice[]") if 'priceList' in request.POST else request.POST.getlist("price[]")
            tax = request.POST.getlist("taxGST[]") if request.POST['place_of_supply'] == com.State else request.POST.getlist("taxIGST[]")
            discount = request.POST.getlist("discount[]")
            total = request.POST.getlist("total[]")

            if len(itemId)==len(itemName)==len(hsn)==len(qty)==len(price)==len(tax)==len(discount)==len(total) and itemId and itemName and hsn and qty and price and tax and discount and total:
                mapped = zip(itemId,itemName,hsn,qty,price,tax,discount,total)
                mapped = list(mapped)
                for ele in mapped:
                    itm = Fin_Items.objects.get(id = int(ele[0]))
                    Fin_Eway_Items.objects.create(Ewaybills = ewaybill, Item = itm, hsn = ele[2], quantity = int(ele[3]), price = float(ele[4]), tax = ele[5], discount = float(ele[6]), total = float(ele[7]))
                    itm.current_stock -= int(ele[3])
                    itm.save()


            Fin_Eway_History.objects.create( 
                Company=com,
                LoginDetails=data,
                Ewaybills=ewaybill,
                action='Created'
            )

            return redirect('Fin_Eway_bills')
        else:
            customers = Fin_Customers.objects.filter(Company=com, status='Active')
            transportations = Fin_Eway_Transportation.objects.filter(Company=com)
            items = Fin_Items.objects.filter(Company=com, status='Active')

            context = {
                'com': com,
                'data': data,
                'customers': customers,
                'Transportation': transportations,
                'items': items,
                'eway_bills': eway_bills,
                'current_date': current_date,
                'allmodules': allmodules,
                'eway_item': eway_item,
            }

            return render(request, 'company/Fin_CreateEwaybill.html', context)
    else:
        return redirect('/')

    
def Fin_EwayOverview(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id=s_id)

        try:
            ewaybill = Fin_Ewaybills.objects.get(Ewaybill_ID=id)
            history = Fin_Eway_History.objects.filter(Ewaybills_id=ewaybill.Ewaybill_ID).last()
            itms = Fin_Eway_Items.objects.filter(Ewaybills=ewaybill)

            try:
                created = Fin_Eway_History.objects.get(Ewaybills=ewaybill, action='Created')
            except Fin_Eway_History.DoesNotExist:
                created = None

            if data.User_Type == "Company":
                com = Fin_Company_Details.objects.get(Login_Id=s_id)
                cmp = com
                allmodules = Fin_Modules_List.objects.get(Login_Id=s_id, status='New')
                cmt = Fin_Eway_Comments.objects.filter(Ewaybill = ewaybill,Company=com)
            else:
                com = Fin_Staff_Details.objects.get(Login_Id=s_id)
                cmp = com.company_id
                allmodules = Fin_Modules_List.objects.get(company_id=com.company_id, status='New')
                cmt = Fin_Eway_Comments.objects.filter(Ewaybill = ewaybill,Company=com.company_id)
                

            return render(request, 'company/Fin_EwayOverview.html', {
                'allmodules': allmodules,
                'com': com,
                'cmp': cmp,
                'data': data,
                'ewaybill': ewaybill,
                'ewayItems': itms,
                'history': history,
                'created': created,
                'comments': cmt,
            })
        except Fin_Ewaybills.DoesNotExist:
            
            return HttpResponse("Ewaybill not found.")
    else:
        return redirect('/')


def Fin_EwayConvert(request,id):
    if 's_id' in request.session:
        ewaybill = Fin_Ewaybills.objects.get(Ewaybill_ID=id)
        ewaybill.Status = 'Saved'
        ewaybill.save()
        return redirect(Fin_EwayOverview, id)


def Fin_EwayHistory(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        ewaybill = Fin_Ewaybills.objects.get(Ewaybill_ID=id)
        history = Fin_Eway_History.objects.filter(Ewaybills_id=ewaybill.Ewaybill_ID)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
        
        return render(request,'company/Fin_EwayHistory.html',{'allmodules':allmodules,'com':com,'data':data,'history':history,'ewaybill': ewaybill,})
    else:
       return redirect('/')


def Fin_EwayDelete(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        ewaybill = Fin_Ewaybills.objects.get(Ewaybill_ID=id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        for i in Fin_Eway_Items.objects.filter(Ewaybills = ewaybill):
            item = Fin_Items.objects.get(id = i.Item.id)
            item.current_stock += i.quantity
            item.save()
        
        Fin_Eway_Items.objects.filter(Ewaybills=ewaybill).delete()
        
        if Fin_Eway_Reference.objects.filter(Company = com).exists():
            deleted = Fin_Eway_Reference.objects.get(Company = com)
            if int(ewaybill.ReferenceNumber) > int(deleted.reference_no):
                deleted.reference_no = ewaybill.ReferenceNumber
                deleted.save()
        else:
            Fin_Eway_Reference.objects.create(Company = com, reference_no = ewaybill.ReferenceNumber)
        
        ewaybill.delete()
        return redirect(Fin_Eway_bills)
    
def Fin_EwayPdf(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        ewaybill = Fin_Ewaybills.objects.get(Ewaybill_ID=id)
        itms = Fin_Eway_Items.objects.filter(Ewaybills = ewaybill)
    
        context = {'ewaybill':ewaybill, 'ewayItems':itms,'cmp':com}
        
        template_path = 'company/Fin_EwayPdf.html'
        fname = 'EwayBill_'+ ewaybill.Ewaybill_No
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] =f'attachment; filename = {fname}.pdf'
        template = get_template(template_path)
        html = template.render(context)


        pisa_status = pisa.CreatePDF(
        html, dest=response)
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
    else:
        return redirect('/')


def Fin_shareEwayToEmail(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        ewaybill = Fin_Ewaybills.objects.get(Ewaybill_ID=id)
        itms = Fin_Eway_Items.objects.filter(Ewaybills = ewaybill)
        try:
            if request.method == 'POST':
                emails_string = request.POST['email_ids']

                emails_list = [email.strip() for email in emails_string.split(',')]
                email_message = request.POST['email_message']
                
                context = {'ewaybill':ewaybill, 'ewayItems':itms,'cmp':com}
                template_path = 'company/Fin_EwayPdf.html'
                template = get_template(template_path)

                html  = template.render(context)
                result = BytesIO()
                pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
                pdf = result.getvalue()
                filename = f'EwayBill_{ewaybill.Ewaybill_No}'
                subject = f"EwayBill_{ewaybill.Ewaybill_No}"
                email = EmailMessage(subject, f"Hi,\nPlease find the attached Invoice for - EWAYBILL-{ewaybill.Ewaybill_No}. \n{email_message}\n\n--\nRegards,\n{com.Company_name}\n{com.Address}\n{com.State} - {com.Country}\n{com.Contact}", from_email=settings.EMAIL_HOST_USER, to=emails_list)
                email.attach(filename, pdf, "application/pdf")
                email.send(fail_silently=False)

                messages.success(request, 'E-WayBill details has been shared via email successfully..!')
                return redirect(Fin_EwayOverview,id)
        except Exception as e:
            print(e)
            messages.error(request, f'{e}')
            return redirect(Fin_EwayOverview, id)


def Fin_EditEway(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            cmp = com
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            cmp = com.company_id

        ewaybill = Fin_Ewaybills.objects.get(Ewaybill_ID=id)
        eway_items = Fin_Eway_Items.objects.filter(Ewaybills = ewaybill)
        cust = Fin_Customers.objects.filter(Company = cmp, status = 'Active')
        items = Fin_Items.objects.filter(Company = cmp, status = 'Active')
        trms = Fin_Company_Payment_Terms.objects.filter(Company = cmp)
        bnk = Fin_Banking.objects.filter(company = cmp)
        lst = Fin_Price_List.objects.filter(Company = cmp, status = 'Active')
        units = Fin_Units.objects.filter(Company = cmp)
        acc = Fin_Chart_Of_Account.objects.filter(Q(account_type='Expense') | Q(account_type='Other Expense') | Q(account_type='Cost Of Goods Sold'), Company=cmp).order_by('account_name')
        transportation = Fin_Eway_Transportation.objects.filter(Company=cmp)

        context = {
            'allmodules':allmodules, 'com':com, 'cmp':cmp, 'data':data,'ewaybill':ewaybill, 'eway_items':eway_items, 'customers':cust, 'items':items, 'pTerms':trms,'list':lst,
            'banks':bnk,'units':units, 'accounts':acc,'transportations':transportation,
        }
        return render(request,'company/Fin_EditEwaybills.html',context)
    else:
       return redirect('/')


logger = logging.getLogger(__name__)
def Fin_EditEwaybills(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id=s_id)

        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id=s_id).company_id

        ewaybill = Fin_Ewaybills.objects.get(Ewaybill_ID=id)

        if request.method == 'POST':
            ewaybill_num = request.POST['Ewaybill_No']

            deliver_to_different_address = request.POST.get('deliver_to_different_address', '0')

            delivery_name = request.POST.get('delivery_name', '')
            delivery_address = request.POST.get('delivery_address', '')
            delivery_phone = request.POST.get('delivery_phone', '')
            delivery_email = request.POST.get('delivery_email', '')
            delivery_place = request.POST.get('delivery_place_of_supply', '')

            if Fin_Ewaybills.objects.filter(Company=com, Ewaybill_No__iexact=ewaybill_num).exclude(Ewaybill_ID=id).exists():
                error_script = f'<script>alert("E-waybill Number `{ewaybill_num}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(error_script)


            # Update Ewaybill fields
            ewaybill.Customer = Fin_Customers.objects.get(id=request.POST['customer'])
            ewaybill.CustomerEmail = request.POST['customer']
            ewaybill.BillingAddress = request.POST['bill_address']
            ewaybill.Customer_PlaceOfSupply = request.POST['place_of_supply']
            ewaybill.Customer_GstNumber = request.POST['gstin']
            ewaybill.Ewaybill_No = ewaybill_num
            ewaybill.Customer_GstType = request.POST['gst_type']
            ewaybill.Date = request.POST['date']
            ewaybill.ReferenceNumber = request.POST['reference_number']
            ewaybill.DocumentType = request.POST['document_type']
            ewaybill.TransactionSubtype = request.POST['transaction_subtype']
            ewaybill.TransactionType = request.POST['transaction_subtype']

            ewaybill.Transportation = Fin_Eway_Transportation.objects.get(id=request.POST['transport_mode'].split(" ")[0])
            ewaybill.VehicleNumber = request.POST['vehicle_number']
            ewaybill.Kilometer = request.POST['kilometer']
            ewaybill.Status = request.POST.get('status', 'Draft')
            ewaybill.SubTotal = 0.0 if request.POST['subtotal'] == "" else float(request.POST['subtotal'])
            ewaybill.Igst = 0.0 if request.POST['igst'] == "" else float(request.POST['igst'])
            ewaybill.Cgst = 0.0 if request.POST['cgst'] == "" else float(request.POST['cgst'])
            ewaybill.Sgst = 0.0 if request.POST['sgst'] == "" else float(request.POST['sgst'])
            ewaybill.TaxAmount = 0.0 if request.POST['taxamount'] == "" else float(request.POST['taxamount'])
            ewaybill.Adjustment = 0.0 if request.POST['adj'] == "" else float(request.POST['adj'])
            ewaybill.ShippingCharge = 0.0 if request.POST['ship'] == "" else float(request.POST['ship'])
            ewaybill.GrandTotal = 0.0 if request.POST['grandtotal'] == "" else float(request.POST['grandtotal'])
            ewaybill.Note = request.POST['note']
            ewaybill.Status="Draft" if 'Draft' in request.POST else "Saved"
            if len(request.FILES) != 0:
                ewaybill.File = request.FILES.get('file')

            if deliver_to_different_address == '1':
                ewaybill.DeliverToDifferentAddress = True
                ewaybill.DeliveryName = delivery_name
                ewaybill.DeliveryAddress = delivery_address
                ewaybill.DeliveryPhone = delivery_phone
                ewaybill.DeliveryEmail = delivery_email
                ewaybill.DeliveryPlace = delivery_place

            if 'Draft' in request.POST:
                ewaybill.Status = "Draft"
            elif 'Save' in request.POST:
                ewaybill.Status = "Saved"

            ewaybill.save()
            logger.debug(f'ewaybill.Transportation: {ewaybill.Transportation}')

            itemId = request.POST.getlist("item_id[]")
            itemName = request.POST.getlist("item_name[]")
            hsn = request.POST.getlist("hsn[]")
            qty = request.POST.getlist("qty[]")
            price = request.POST.getlist("priceListPrice[]") if 'priceList' in request.POST else request.POST.getlist("price[]")
            tax = request.POST.getlist("taxGST[]") if request.POST['place_of_supply'] == com.State else request.POST.getlist("taxIGST[]")
            discount = request.POST.getlist("discount[]")
            total = request.POST.getlist("total[]")
            eway_item_ids = request.POST.getlist("id[]")
            ewayItem_ids = [int(id) for id in eway_item_ids]

            eway_items = Fin_Eway_Items.objects.filter(Ewaybills=ewaybill)
            object_ids = [obj.id for obj in eway_items]

            ids_to_delete = [obj_id for obj_id in object_ids if obj_id not in ewayItem_ids]
            for itmId in ids_to_delete:
                ewayItem = Fin_Eway_Items.objects.get(id=itmId)
                item = Fin_Items.objects.get(id=ewayItem.Item.id)
                item.current_stock += ewayItem.quantity
                item.save()

            Fin_Eway_Items.objects.filter(id__in=ids_to_delete).delete()

            count = Fin_Eway_Items.objects.filter(Ewaybills=ewaybill).count()

            if len(itemId) == len(itemName) == len(hsn) == len(qty) == len(price) == len(tax) == len(discount) == len(total) == len(
                    ewayItem_ids) and ewayItem_ids and itemId and itemName and hsn and qty and price and tax and discount and total:
                mapped = zip(itemId, itemName, hsn, qty, price, tax, discount, total, ewayItem_ids)
                mapped = list(mapped)
                for ele in mapped:
                    if int(len(itemId)) > int(count):
                        if ele[8] == 0:
                            itm = Fin_Items.objects.get(id=int(ele[0]))
                            Fin_Eway_Items.objects.create(Ewaybills=ewaybill, Item=itm, hsn=ele[2],
                                                        quantity=int(ele[3]), price=float(ele[4]), tax=ele[5],
                                                        discount=float(ele[6]), total=float(ele[7]))
                            itm.current_stock -= int(ele[3])
                            itm.save()
                        else:
                            itm = Fin_Items.objects.get(id=int(ele[0]))
                            inItm = Fin_Eway_Items.objects.get(id=int(ele[8]))
                            crQty = int(inItm.quantity)

                            Fin_Eway_Items.objects.filter(id=int(ele[8])).update(Ewaybills=ewaybill, Item=itm,
                                                                                hsn=ele[2], quantity=int(ele[3]),
                                                                                price=float(ele[4]), tax=ele[5],
                                                                                discount=float(ele[6]), total=float(ele[7]))

                            if crQty < int(ele[3]):
                                itm.current_stock -= abs(crQty - int(ele[3]))
                            elif crQty > int(ele[3]):
                                itm.current_stock += abs(crQty - int(ele[3]))
                            itm.save()
                    else:
                        itm = Fin_Items.objects.get(id=int(ele[0]))
                        inItm = Fin_Eway_Items.objects.get(id=int(ele[8]))
                        crQty = int(inItm.quantity)

                        Fin_Eway_Items.objects.filter(id=int(ele[8])).update(Ewaybills=ewaybill, Item=itm,
                                                                            hsn=ele[2], quantity=int(ele[3]),
                                                                            price=float(ele[4]), tax=ele[5],
                                                                            discount=float(ele[6]), total=float(ele[7]))

                        if crQty < int(ele[3]):
                            itm.current_stock -= abs(crQty - int(ele[3]))
                        elif crQty > int(ele[3]):
                            itm.current_stock += abs(crQty - int(ele[3]))
                        itm.save()

            logger.debug(f'eway_items: {eway_items}')
            logger.debug(f'items: {itm}')

            
            Fin_Eway_History.objects.create(
                Company=com,
                LoginDetails=data,
                Ewaybills=ewaybill,
                action='Edited'
            )

            return redirect('Fin_EwayOverview', id)
        else:
            return redirect('Fin_EditEway', id)
    else:
        return redirect('/')
        
def Fin_attachEwaybillFile(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        ewaybill = Fin_Ewaybills.objects.get(Ewaybill_ID=id)

        if request.method == 'POST' and len(request.FILES) != 0:
            ewaybill.File = request.FILES.get('file')
            ewaybill.save()

        return redirect(Fin_EwayOverview, id)
    else:
        return redirect('/')

def Fin_addEwayComment(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        ewaybill = Fin_Ewaybills.objects.get(Ewaybill_ID=id)

        if request.method == "POST":
            cmt = request.POST['comment'].strip()

            Fin_Eway_Comments.objects.create(Company = com, Ewaybill = ewaybill, comments = cmt)

            return redirect(Fin_EwayOverview, id)
        return redirect(Fin_EwayOverview, id)
    return redirect('/') 
    
def Fin_deleteEwayComment(request,id):
    if 's_id' in request.session:
        cmt = Fin_Eway_Comments.objects.get(id = id)
        ewaybillId = cmt.Ewaybill.Ewaybill_ID
        cmt.delete()
        return redirect(Fin_EwayOverview, ewaybillId)
#END


#---------------------------- Purchase Bill --------------------------------# 

def Fin_List_Purchase_Bill(request):
    s_id = request.session['s_id']
    data = Fin_Login_Details.objects.get(id = s_id)
    if data.User_Type == "Company":
        com = Fin_Company_Details.objects.get(Login_Id = s_id)
        allmodules = Fin_Modules_List.objects.get(Login_Id = s_id)
    else:
        com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        allmodules = Fin_Modules_List.objects.get(Login_Id = com.id)
    pbill = Fin_Purchase_Bill.objects.filter(company=com)
    context = {'allmodules':allmodules, 'data':data, 'com':com, 'pbill':pbill}
    return render(request,'company/Fin_Pbill_List.html', context)
    
def Fin_List_Purchase_Add(request):
    s_id = request.session['s_id']
    data = Fin_Login_Details.objects.get(id = s_id)
    if data.User_Type == "Company":
        com = Fin_Company_Details.objects.get(Login_Id = s_id)
        allmodules = Fin_Modules_List.objects.get(Login_Id = s_id)
    else:
        com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        allmodules = Fin_Modules_List.objects.get(Login_Id = com.id)
    ven = Fin_Vendors.objects.filter(Company = com, status = 'Active')
    cust = Fin_Customers.objects.filter(Company = com, status = 'Active')
    bnk = Fin_Banking.objects.filter(company = com, bank_status = 'Active')
    itm = Fin_Items.objects.filter(Company = com, status = 'Active')
    plist = Fin_Price_List.objects.filter(Company = com, type = 'Purchase', status = 'Active')
    terms = Fin_Company_Payment_Terms.objects.filter(Company = com)
    units = Fin_Units.objects.filter(Company = com)
    account = Fin_Chart_Of_Account.objects.filter(Q(account_type='Expense') | Q(account_type='Other Expense') | Q(account_type='Cost Of Goods Sold'), Company=com).order_by('account_name')
    tod = datetime.now().strftime('%Y-%m-%d')
    if Fin_Purchase_Bill.objects.filter(company = com):
        try:
            ref_no = int(Fin_Purchase_Bill_Ref_No.objects.filter(company = com).last().ref_no) + 1
        except:
            ref_no =  1
        bill_no = Fin_Purchase_Bill.objects.filter(company = com).last().bill_no
        match = re.search(r'^(\d+)|(\d+)$', bill_no)
        if match:
            numeric_part = match.group(0)
            incremented_numeric = str(int(numeric_part) + 1).zfill(len(numeric_part))
            bill_no = re.sub(r'\d+', incremented_numeric, bill_no, count=1)
    else:
        try:
            ref_no = int(Fin_Purchase_Bill_Ref_No.objects.filter(company = com).last().ref_no) + 1
        except:
            ref_no =  1
        bill_no = 1000
    context = {'allmodules':allmodules, 'data':data, 'com':com, 'ven':ven, 'cust':cust, 'bnk':bnk, 'units':units,
               'account':account, 'itm':itm, 'tod':tod, 'plist':plist, 'ref_no': ref_no, 'bill_no':bill_no, 'terms':terms}
    return render(request,'company/Fin_Pbill_Add.html', context)

def Fin_Price_List_Data(request):
    plist_id = request.GET.get('plist_id')
    itm_id = request.GET.get('itm_id')
    plist = Fin_Price_List.objects.get(id=plist_id)
    itm = Fin_Items.objects.get(id=itm_id)
    if plist.item_rate == 'Markup/Markdown by a percentage':
        if plist.up_or_down == 'Markup':
            price = float(itm.purchase_price) + (float(itm.purchase_price)*float(plist.percentage)/100)
        else:
            price = float(itm.purchase_price) - (float(itm.purchase_price)*float(plist.percentage)/100)
    else:
        try:
            price = Fin_PriceList_Items.objects.get(list = plist, item = itm).custom_rate
        except:
            price = itm.purchase_price
    return JsonResponse({'price':price})
    
def Fin_Create_Purchase_Bill(request):
  if request.method == 'POST': 
    s_id = request.session['s_id']
    data = Fin_Login_Details.objects.get(id = s_id)
    if data.User_Type == "Company":
        com = Fin_Company_Details.objects.get(Login_Id = s_id)
    else:
        com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
    
    ven = Fin_Vendors.objects.get(id = request.POST.get('ven_name'))
    if request.POST.get('cust_name') == "" or request.POST.get('cust_name') == 'none':
        cust = None
    else:
        cust = Fin_Customers.objects.get(id = request.POST.get('cust_name'))
    plist = None if request.POST.get('price_list') == "" else Fin_Price_List.objects.get(id = request.POST.get('price_list'))
    term = None if request.POST.get('pay_terms') == "" else Fin_Company_Payment_Terms.objects.get(id = request.POST.get('pay_terms'))
    pbill = Fin_Purchase_Bill(vendor = ven,
                              customer = cust,
                              pricelist = plist,
                              ven_psupply = request.POST.get('ven_psupply'),
                              cust_psupply = request.POST.get('cust_psupply'),
                              bill_no = request.POST.get('bill_no'),
                              ref_no = request.POST.get('ref_no'),
                            #   porder_no = request.POST.get('pord_no'),
                              bill_date = request.POST.get('bill_date'),
                              due_date = request.POST.get('due_date'),
                              pay_term = term,
                              pay_type = request.POST.get('pay_type'),
                              cheque_no = request.POST.get('cheque_id'),
                              upi_no = request.POST.get('upi_id'),
                              bank_no = request.POST.get('bnk_no'),
                              subtotal = request.POST.get('sub_total'),
                              igst = request.POST.get('igst'),
                              cgst = request.POST.get('cgst'),
                              sgst = request.POST.get('sgst'),
                              taxamount = request.POST.get('tax_amount'),
                              ship_charge = request.POST.get('shipcharge'),
                              adjust = request.POST.get('adjustment'),
                              grandtotal = request.POST.get('grand_total'),
                              paid = request.POST.get('paid'),
                              balance = request.POST.get('bal_due'),
                              company = com,
                              logindetails = data)
    if 'Draft' in request.POST:
        pbill.status = "Draft"
    if "Save" in request.POST:
        pbill.status = "Save"  
    if len(request.FILES) != 0:
        pbill.file=request.FILES.get('file')  

    pbill.save()
        
    item = tuple(request.POST.getlist("product[]"))
    qty =  tuple(request.POST.getlist("qty[]"))
    price =  tuple(request.POST.getlist("price[]"))
    if request.POST.getlist("intra_tax[]")[0] != '':
        tax = tuple(request.POST.getlist("intra_tax[]"))
    else:
        tax = tuple(request.POST.getlist("inter_tax[]"))
    discount =  tuple(request.POST.getlist("discount[]"))
    total =  tuple(request.POST.getlist("total[]"))

    if len(item)==len(qty)==len(price)==len(tax)==len(discount)==len(total):
        mapped=zip(item,qty,price,tax,discount,total)
        mapped=list(mapped)
        for ele in mapped:
            itm = Fin_Items.objects.get(id=ele[0])
            Fin_Purchase_Bill_Item.objects.create(item = itm,qty = ele[1],price = ele[2],tax = ele[3],discount = ele[4],total = ele[5],pbill = pbill,company = com)
            itm.current_stock = int(itm.current_stock) + int(ele[1])
            itm.save()

    Fin_Purchase_Bill_Ref_No.objects.create(company = com, logindetails = data, ref_no = request.POST.get('ref_no'))
    Fin_Purchase_Bill_History.objects.create(company =com, logindetails = data, pbill = pbill, action='Created')
    return redirect('Fin_List_Purchase_Bill')
  else:
    return redirect('Fin_List_Purchase_Add')
  
def Fin_Check_Pbill_No(request):
    s_id = request.session['s_id']
    data = Fin_Login_Details.objects.get(id = s_id)
    if data.User_Type == "Company":
        com = Fin_Company_Details.objects.get(Login_Id = s_id)
    else:
        com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

    bill_no = request.GET.get('no')
    id = request.GET.get('id')
    if id:
        bill_list = Fin_Purchase_Bill.objects.filter(company = com).exclude(id = id)
    else:
        bill_list = Fin_Purchase_Bill.objects.filter(company = com)
    for b in bill_list:
        if str(b.bill_no).upper() == str(bill_no).upper():
            return JsonResponse({'message':'Used'})

    bill = re.search(r'[a-zA-Z]+', bill_no)
    if bill:
        bill = bill.group()

    sale_no = Fin_Sales_Order.objects.filter(Company = com)
    for no in sale_no:
        sale = re.search(r'[a-zA-Z]+', no.sales_order_no)
        if sale:
            sale = sale.group()
        if sale.upper() == bill.upper():
            return JsonResponse({'message':'Invalid'})
    return JsonResponse({'message':'Valid'})

def Fin_New_Vendor(request):
    s_id = request.session['s_id']
    data = Fin_Login_Details.objects.get(id = s_id)
    if data.User_Type == "Company":
        com = Fin_Company_Details.objects.get(Login_Id = s_id)
    else:
        com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

    if request.method == 'GET':
        vnd = Fin_Vendors(
            Company = com,
            LoginDetails = com.Login_Id,
            title = request.GET.get('title'),
            first_name = request.GET.get('fname'),
            last_name = request.GET.get('lname'),
            company = request.GET.get('cname'),
            location = request.GET.get('loc'),
            email = request.GET.get('email'),
            website = request.GET.get('site'),
            mobile = request.GET.get('phone'),
            gst_type = request.GET.get('gst_type'),
            gstin = None if request.GET.get('gst_type') == "Unregistered Business" or request.GET.get('gst_type') == 'Overseas' or request.GET.get('gst_type') == 'Consumer' else request.GET.get('gst_in'),
            pan_no = request.GET.get('pan'),
            place_of_supply = request.GET.get('psupply'),
            currency = request.GET.get('currency'),
            open_balance_type = request.GET.get('bal_type'),
            opening_balance = 0 if request.GET.get('bal') == "" else float(request.GET.get('bal')),
            current_balance = 0 if request.GET.get('bal') == "" else float(request.GET.get('bal')),
            credit_limit = 0 if request.GET.get('limit') == "" else float(request.GET.get('limit')),
            payment_terms = None if request.GET.get('terms') == "" else Fin_Company_Payment_Terms.objects.get(id = request.GET.get('terms')),
            price_list = None if request.GET.get('plist') ==  "" else Fin_Price_List.objects.get(id = request.GET.get('plist')),
            billing_street = request.GET.get('street'),
            billing_city = request.GET.get('city'),
            billing_state = request.GET.get('state'),
            billing_pincode = request.GET.get('pinco'),
            billing_country = request.GET.get('country'),
            ship_street = request.GET.get('shipstreet'),
            ship_city = request.GET.get('shipcity'),
            ship_state = request.GET.get('shipstate'),
            ship_pincode = request.GET.get('shippinco'),
            ship_country = request.GET.get('shipcountry'),
            status = 'Active'
        )
        vnd.save()

        Fin_Vendor_History.objects.create(
            Company = com,
            LoginDetails = data,
            Vendor = vnd,
            action = 'Created'
        )
        return JsonResponse({'id':vnd.id})

    else:
        return JsonResponse({'message':'Error'})

def Fin_New_Customer(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        if request.method == 'GET':
            cust = Fin_Customers(
                Company = com,
                LoginDetails = data,
                title = request.GET.get('title'),
                first_name = request.GET.get('fname'),
                last_name = request.GET.get('lname'),
                company = request.GET.get('cname'),
                location = request.GET.get('loc'),
                place_of_supply = request.GET.get('psupply'),
                gst_type = request.GET.get('gst_type'),
                gstin = None if request.GET.get('gst_type') == "Unregistered Business" or request.GET.get('gst_type') == 'Overseas' or request.GET.get('gst_type') == 'Consumer' else request.GET.get('gst_in'),
                pan_no = request.GET.get('pan'),
                email = request.GET.get('email'),
                mobile = request.GET.get('phone'),
                website = request.GET.get('site'),
                price_list = None if request.GET.get('plist') ==  "" else Fin_Price_List.objects.get(id = request.GET.get('plist')),
                payment_terms = None if request.GET.get('terms') == "" else Fin_Company_Payment_Terms.objects.get(id = request.GET.get('terms')),
                opening_balance = 0 if request.GET.get('bal') == "" else float(request.GET.get('bal')),
                open_balance_type = request.GET.get('bal_type'),
                current_balance = 0 if request.GET.get('bal') == "" else float(request.GET.get('bal')),
                credit_limit = 0 if request.GET.get('limit') == "" else float(request.GET.get('limit')),
                billing_street = request.GET.get('street'),
                billing_city = request.GET.get('city'),
                billing_state = request.GET.get('state'),
                billing_pincode = request.GET.get('pinco'),
                billing_country = request.GET.get('country'),
                ship_street = request.GET.get('shipstreet'),
                ship_city = request.GET.get('shipcity'),
                ship_state = request.GET.get('shipstate'),
                ship_pincode = request.GET.get('shippinco'),
                ship_country = request.GET.get('shipcountry'),
                status = 'Active'
            )
            cust.save()

            Fin_Customers_History.objects.create(
                Company = com,
                LoginDetails = data,
                customer = cust,
                action = 'Created'
            )

        return JsonResponse({'id':cust.id})
    else:
        return JsonResponse({'message':'Error'})

def Fin_New_Payment_Term(request):
    s_id = request.session['s_id']
    data = Fin_Login_Details.objects.get(id = s_id)
    if data.User_Type == "Company":
        com = Fin_Company_Details.objects.get(Login_Id = s_id)
    else:
        com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
    days = request.GET.get('days')
    term_name = request.GET.get('term_name')
    terms = Fin_Company_Payment_Terms.objects.create(Company = com, term_name = term_name, days = days)
    return JsonResponse({'id':terms.id})

def Fin_Check_New_Item_Name(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        name = request.POST['itm_name']

        if Fin_Items.objects.filter(Company = com, name__iexact = name).exists():
            msg = f'{name} already exists, Try another.!'
            return JsonResponse({'is_exist':True, 'message':msg})
        else:
            return JsonResponse({'is_exist':False})
    else:
        return redirect('/')

def Fin_Check_New_Item_HSN(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        hsn = request.POST['itm_hsn']

        if Fin_Items.objects.filter(Company = com, hsn__iexact = hsn).exists():
            msg = f'{hsn} already exists, Try another.!'
            return JsonResponse({'is_exist':True, 'message':msg})
        else:
            return JsonResponse({'is_exist':False})
    else:
        return redirect('/')

def Fin_New_Item(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        if request.method == 'GET':
            name = request.GET.get('name')
            type = request.GET.get('type')
            unit = request.GET.get('unit')
            hsn = request.GET.get('hsn')
            tax = request.GET.get('taxref')
            gstTax = 0 if tax == 'non taxable' else request.GET.get('intra_st')
            igstTax = 0 if tax == 'non taxable' else request.GET.get('inter_st')
            purPrice = request.GET.get('pcost')
            purAccount = None if not 'pur_account' in request.GET or request.GET.get('pur_account') == "" else request.GET.get('pur_account')
            purDesc = request.GET.get('pur_desc')
            salePrice = request.GET.get('salesprice')
            saleAccount = None if not 'sale_account' in request.GET or request.GET.get('sale_account') == "" else request.GET.get('sale_account')
            saleDesc = request.GET.get('sale_desc')
            inventory = request.GET.get('invacc')
            stock = 0 if request.GET.get('stock') == "" else request.GET.get('stock')
            stockUnitRate = 0 if request.GET.get('stock_rate') == "" else request.GET.get('stock_rate')
            minStock = request.GET.get('min_stock')
            createdDate = date.today()
            
            item = Fin_Items(
                Company = com,
                LoginDetails = data,
                name = name,
                item_type = type,
                unit = unit,
                hsn = hsn,
                tax_reference = tax,
                intra_state_tax = gstTax,
                inter_state_tax = igstTax,
                sales_account = saleAccount,
                selling_price = salePrice,
                sales_description = saleDesc,
                purchase_account = purAccount,
                purchase_price = purPrice,
                purchase_description = purDesc,
                item_created = createdDate,
                min_stock = minStock,
                inventory_account = inventory,
                opening_stock = stock,
                current_stock = stock,
                stock_in = 0,
                stock_out = 0,
                stock_unit_rate = stockUnitRate,
                status = 'Active'
            )
            item.save()

            Fin_Items_Transaction_History.objects.create(
                Company = com,
                LoginDetails = data,
                item = item,
                action = 'Created'
            )
                
            return JsonResponse({'id': item.id})
        return JsonResponse({'message':'Error'})

def Fin_View_Purchase_Bill(request,id):
    s_id = request.session['s_id']
    data = Fin_Login_Details.objects.get(id = s_id)
    if data.User_Type == "Company":
        com = Fin_Company_Details.objects.get(Login_Id = s_id)
        allmodules = Fin_Modules_List.objects.get(Login_Id = s_id)
    else:
        com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        allmodules = Fin_Modules_List.objects.get(Login_Id = com.id)
    pbill = Fin_Purchase_Bill.objects.get(id=id)
    itm = Fin_Purchase_Bill_Item.objects.filter(pbill=pbill)
    hist = Fin_Purchase_Bill_History.objects.get(company = com, pbill = pbill, action = 'Created')
    comments = Fin_Purchase_Bill_Comment.objects.filter(pbill = pbill)
    context = {'allmodules':allmodules, 'data':data, 'com':com,'pbill':pbill, 'itm':itm, 'hist':hist, 'comments':comments }
    return render(request, 'company/Fin_Pbill_View.html', context)

def Fin_Purchase_Bill_Edit(request,id):
    s_id = request.session['s_id']
    data = Fin_Login_Details.objects.get(id = s_id)
    if data.User_Type == "Company":
        com = Fin_Company_Details.objects.get(Login_Id = s_id)
        allmodules = Fin_Modules_List.objects.get(Login_Id = s_id)
    else:
        com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        allmodules = Fin_Modules_List.objects.get(Login_Id = com.id)
    ven = Fin_Vendors.objects.filter(Company = com, status = 'Active')
    cust = Fin_Customers.objects.filter(Company = com, status = 'Active')
    bnk = Fin_Banking.objects.filter(company = com, bank_status = 'Active')
    itm = Fin_Items.objects.filter(Company = com, status = 'Active')
    plist = Fin_Price_List.objects.filter(Company = com, type = 'Purchase', status = 'Active')
    terms = Fin_Company_Payment_Terms.objects.filter(Company = com)
    units = Fin_Units.objects.filter(Company = com)
    account = Fin_Chart_Of_Account.objects.filter(Q(account_type='Expense') | Q(account_type='Other Expense') | Q(account_type='Cost Of Goods Sold'), Company=com).order_by('account_name')
    pbill = Fin_Purchase_Bill.objects.get(id = id)
    pitm = Fin_Purchase_Bill_Item.objects.filter(pbill = pbill)
    bill_no = pbill.bill_no
    context = {'allmodules':allmodules, 'data':data, 'com':com, 'ven':ven, 'cust':cust, 'bnk':bnk, 'units':units,'pbill':pbill, 'bill_no':bill_no,
               'account':account, 'itm':itm, 'plist':plist, 'terms':terms, 'pitm':pitm}
    return render(request, 'company/Fin_Pbill_Edit.html', context)

def Fin_Update_Purchase_Bill(request, id):
    if request.method == 'POST': 
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        ven = Fin_Vendors.objects.get(id = request.POST.get('ven_name'))
        if request.POST.get('cust_name') == "" or request.POST.get('cust_name') == 'none':
            cust = None
        else:
            cust = Fin_Customers.objects.get(id = request.POST.get('cust_name'))
        plist = None if request.POST.get('price_list') == "" else Fin_Price_List.objects.get(id = request.POST.get('price_list'))
        term = None if request.POST.get('pay_terms') == "" else Fin_Company_Payment_Terms.objects.get(id = request.POST.get('pay_terms'))
        pbill = Fin_Purchase_Bill.objects.get(id = id)

        pbill.vendor = ven
        pbill.customer = cust
        pbill.pricelist = plist
        pbill.ven_psupply = request.POST.get('ven_psupply')
        pbill.cust_psupply = request.POST.get('cust_psupply')
        pbill.bill_no = request.POST.get('bill_no')
        pbill.ref_no = request.POST.get('ref_no')
    #   pbill.porder_no = request.POST.get('pord_no')
        pbill.bill_date = request.POST.get('bill_date')
        pbill.due_date = request.POST.get('due_date')
        pbill.pay_term = term
        pbill.pay_type = request.POST.get('pay_type')
        pbill.cheque_no = request.POST.get('cheque_id')
        pbill.upi_no = request.POST.get('upi_id')
        pbill.bank_no = request.POST.get('bnk_no')
        pbill.subtotal = request.POST.get('sub_total')
        pbill.igst = request.POST.get('igst')
        pbill.cgst = request.POST.get('cgst')
        pbill.sgst = request.POST.get('sgst')
        pbill.taxamount = request.POST.get('tax_amount')
        pbill.ship_charge = request.POST.get('shipcharge')
        pbill.adjust = request.POST.get('adjustment')
        pbill.grandtotal = request.POST.get('grand_total')
        pbill.paid = request.POST.get('paid')
        pbill.balance = request.POST.get('bal_due')
        pbill.company = com
        pbill.logindetails = data

        if len(request.FILES) != 0:
            pbill.file=request.FILES.get('file')  

        pbill.save()
            
        bill_item_list = Fin_Purchase_Bill_Item.objects.filter(company = com, pbill = pbill)
        for bill_item in bill_item_list:
            bill_item.item.current_stock = bill_item.item.current_stock - bill_item.qty
            bill_item.item.save()
        bill_item_list.delete()

        item = tuple(request.POST.getlist("product[]"))
        qty =  tuple(request.POST.getlist("qty[]"))
        price =  tuple(request.POST.getlist("price[]"))
        if request.POST.getlist("intra_tax[]")[0] != '':
            tax = tuple(request.POST.getlist("intra_tax[]"))
        else:
            tax = tuple(request.POST.getlist("inter_tax[]"))
        discount =  tuple(request.POST.getlist("discount[]"))
        total =  tuple(request.POST.getlist("total[]"))

        if len(item)==len(qty)==len(price)==len(tax)==len(discount)==len(total):
            mapped=zip(item,qty,price,tax,discount,total)
            mapped=list(mapped)
            for ele in mapped:
                itm = Fin_Items.objects.get(id=ele[0])
                Fin_Purchase_Bill_Item.objects.create(item = itm,qty = ele[1],price = ele[2],tax = ele[3],discount = ele[4],total = ele[5],pbill = pbill,company = com)
                itm.current_stock = int(itm.current_stock) + int(ele[1])
                itm.save()

        Fin_Purchase_Bill_History.objects.create(company =com, logindetails = data, pbill = pbill, action='Updated')
        return redirect('Fin_View_Purchase_Bill', id)
    else:
        return redirect('Fin_View_Purchase_Bill', id)

def Fin_Purchase_Bill_Add_Edit_Comment(request, id):
    s_id = request.session['s_id']
    data = Fin_Login_Details.objects.get(id = s_id)
    if data.User_Type == "Company":
        com = Fin_Company_Details.objects.get(Login_Id = s_id)
    else:
        com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
    pbill = Fin_Purchase_Bill.objects.get(id = id)
    if 'comment_save' in request.POST:
        pbill_com = Fin_Purchase_Bill_Comment(company = com,
                                            logindetails = data,
                                            comment = request.POST.get('comment'),
                                            pbill = pbill)
        pbill_com.save()
    else:
        com_id = request.POST.get('comment_id')
        comm = Fin_Purchase_Bill_Comment.objects.get(id = com_id)
        comm.logindetails = data
        comm.comment = request.POST.get('comment')
        comm.save()
    return redirect('Fin_View_Purchase_Bill', id)

def Fin_Purchase_Bill_Delete_Comment(request, id):
    comm = Fin_Purchase_Bill_Comment.objects.get(id = id)
    bill = comm.pbill.id
    comm.delete()
    return redirect('Fin_View_Purchase_Bill', bill)

def Fin_Delete_Purchase_Bill(request,id):
    pbill = Fin_Purchase_Bill.objects.get(id=id)
    Fin_Purchase_Bill_Item.objects.filter(pbill = pbill).delete()
    Fin_Purchase_Bill_History.objects.filter(pbill = pbill).delete()
    Fin_Purchase_Bill_Comment.objects.filter(pbill = pbill).delete()
    pbill.delete()
    return redirect('Fin_List_Purchase_Bill')

def Fin_Add_Additional_Files(request,id):
    pbill = Fin_Purchase_Bill.objects.get(id=id)
    if request.method == 'POST':
        if len(request.FILES) != 0:
            pbill.file = request.FILES['file']
            pbill.save()
        return redirect('Fin_View_Purchase_Bill',id)
    
def Fin_Purchase_List_History(request,id):
    s_id = request.session['s_id']
    data = Fin_Login_Details.objects.get(id = s_id)
    if data.User_Type == "Company":
        com = Fin_Company_Details.objects.get(Login_Id = s_id)
        allmodules = Fin_Modules_List.objects.get(Login_Id = s_id)
    else:
        com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        allmodules = Fin_Modules_List.objects.get(Login_Id = com.id)
    pbill = Fin_Purchase_Bill.objects.get(id=id)
    hist = Fin_Purchase_Bill_History.objects.filter(company = com, pbill = pbill)
    context = {'allmodules':allmodules, 'data':data, 'com':com, 'hist':hist, 'pbill':pbill}
    return render(request, 'company/Fin_Pbill_History.html', context)

def Fin_Convert_To_Active(request,id):
    pbill = Fin_Purchase_Bill.objects.get(id = id)
    pbill.status = 'Save'
    pbill.save()
    return redirect('Fin_View_Purchase_Bill', id)
    
#End


# -------------------------- admin new updates ------------------------------------ 

def Fin_remove_payment_terms(request,pk):
    payment_term=Fin_Payment_Terms.objects.get(id=pk)
    payment_term.delete()
    messages.success(request, 'Payment term is removed')
    return redirect('Fin_PaymentTerm')

def Fin_Clients_under_distributors(request):
   distributors=Fin_Distributors_Details.objects.filter(Admin_approval_status="Accept")
   noti = Fin_ANotification.objects.filter(status = 'New').order_by('-id','-Noti_date')
   n = len(noti)

   context={
        'noti':noti,
        'n':n,
        'distributors':distributors
    }
   return render(request,"Admin/Fin_clients_under_distributors.html", context)

def get_clients_under_distributor(request):
  if request.method == 'GET':
    distributor_id = request.GET.get('distributor_id')
    
    # Query your database to fetch employee details based on the employee_id.

    company = Fin_Company_Details.objects.filter(Distributor_id=distributor_id,Distributor_approval_status='Accept').order_by('-id')
    company_details=[]

    for i in company:
      cmp_id=i.id
      fname=i.Login_Id.First_name 
      lname=i.Login_Id.Last_name
      email=i.Email
      contact=i.Contact
      pterm_no=i.Payment_Term.payment_terms_number if i.Payment_Term else 'Trial'
      pterm_value=i.Payment_Term.payment_terms_value if i.Payment_Term else 'Period'
      sdate=i.Start_Date
      edate=i.End_date

      company_details.append({
        'cmp_id':cmp_id,
        'fname':fname,
        'lname':lname,
        'email':email,
        'contact':contact,
        'pterm_no':pterm_no,
        'pterm_value':pterm_value,
        'sdate':sdate,
        'edate':edate
      })
    
    # You might want to serialize the 'company_details' to a JSON format.
    return JsonResponse({'details': company_details})

  else:
    return JsonResponse({'error': 'Invalid request method.'}, status=400)


def distributor_client_profile_details(request,pk):
    data = Fin_Company_Details.objects.get(id=pk)
    allmodules = Fin_Modules_List.objects.get(company_id = pk,status = "New")
    noti = Fin_ANotification.objects.filter(status = 'New').order_by('-id','-Noti_date')
    n = len(noti)
 

    context={
        'data':data,'allmodules':allmodules,'noti':noti,'n':n
    }

    return render(request,'Admin/distributor_client_profile_details.html',context)

# ----Trial period section------

def Fin_Admin_trial_period_section(request):
    noti = Fin_ANotification.objects.filter(status = 'New').order_by('-id','-Noti_date')
    n = len(noti)
    context = {
        'noti':noti,
        'n':n
    }
    return render(request,'Admin/Fin_Admin_trial_period_section.html', context)


def Fin_Admin_trial_period_clients(request):
    noti = Fin_ANotification.objects.filter(status = 'New').order_by('-id','-Noti_date')
    n = len(noti)
    clients=TrialPeriod.objects.filter(company__Registration_Type='self',company__Admin_approval_status='Accept').order_by('-id')
    context={
        'clients':clients,
        'noti':noti,
        'n':n
    }
    return render(request,'Admin/Fin_Admin_trial_period_clients.html', context)


def Fin_Admin_trial_period_distributor_clients(request):
    noti = Fin_ANotification.objects.filter(status = 'New').order_by('-id','-Noti_date')
    n = len(noti)
    distributors=Fin_Distributors_Details.objects.filter(Admin_approval_status='Accept')
    clients=TrialPeriod.objects.filter(company__Registration_Type='distributor',company__Distributor_approval_status='Accept').order_by('-id')
    context={
        'clients':clients,
        'distributors':distributors,
        'noti':noti,
        'n':n
    }
    return render(request,'Admin/Fin_Admin_trial_period_distributor_clients.html', context)

# ---------------------------end admin updates------------------------------------ 


# --------------------------- distributor new updates------------------------------------
  
# ----Trial period section------

def Fin_trial_periodclients(request):

    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Distributors_Details.objects.get(Login_Id = s_id)
        com = Fin_Distributors_Details.objects.get(Login_Id = s_id)
        noti = Fin_DNotification.objects.filter(status = 'New',Distributor_id =com)
        n = len(noti)

        clients=TrialPeriod.objects.filter(company__Distributor_id=com,company__Distributor_approval_status='Accept').order_by('-id')
        context={
            'data':data,
            'com': com,
            'clients':clients,
            'n':n,
            'noti':noti

        }
        return render(request,'Distributor/Fin_trial_period_client.html', context)
    else:
        return redirect('/')

      
# ---------------------------end distributor updates------------------------------------  


#------------- company new updates-------------------

def Fin_company_trial_feedback(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        com = Fin_Company_Details.objects.get(Login_Id = s_id)
        trial_instance = TrialPeriod.objects.get(company=com)
        if request.method == 'POST':
            interested = request.POST.get('interested')
            feedback=request.POST.get('feedback') 
            
            trial_instance.interested_in_buying=1 if interested == 'yes' else 2
            trial_instance.feedback=feedback
            trial_instance.save()

            if interested =='yes':
                return redirect('Fin_Company_Profile')
            else:
                return redirect('Fin_Company_Profile')
        else:
            return redirect('Fin_Com_Home')
    else:
        return redirect('/')
        
# ---------------------------end company updates------------------------------------  


# < ------------- Shemeem -------- > Estimates < ------------------------------- >
        
def Fin_estimates(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            cmp = com
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            cmp = com.company_id
        
        allmodules = Fin_Modules_List.objects.get(company_id = cmp,status = 'New')
        est = Fin_Estimate.objects.filter(Company = cmp)
        return render(request,'company/Fin_Estimate.html',{'allmodules':allmodules,'com':com, 'cmp':cmp,'data':data,'estimates':est})
    else:
       return redirect('/')

def Fin_addEstimate(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            cmp = com
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            cmp = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = cmp,status = 'New')
        cust = Fin_Customers.objects.filter(Company = cmp, status = 'Active')
        itms = Fin_Items.objects.filter(Company = cmp, status = 'Active')
        trms = Fin_Company_Payment_Terms.objects.filter(Company = cmp)
        lst = Fin_Price_List.objects.filter(Company = cmp, status = 'Active')
        units = Fin_Units.objects.filter(Company = cmp)
        acc = Fin_Chart_Of_Account.objects.filter(Q(account_type='Expense') | Q(account_type='Other Expense') | Q(account_type='Cost Of Goods Sold'), Company=cmp).order_by('account_name')

        # Fetching last Estimate and assigning upcoming ref no as current + 1
        # Also check for if any bill is deleted and ref no is continuos w r t the deleted Estimate
        latest_est = Fin_Estimate.objects.filter(Company = cmp).order_by('-id').first()

        new_number = int(latest_est.reference_no) + 1 if latest_est else 1

        if Fin_Estimate_Reference.objects.filter(Company = cmp).exists():
            deleted = Fin_Estimate_Reference.objects.get(Company = cmp)
            
            if deleted:
                while int(deleted.reference_no) >= new_number:
                    new_number+=1

        # Finding next EST number w r t last EST number if exists.
        nxtEST = ""
        # lastEST = Fin_Estimate.objects.filter(Company = cmp).last()
        if latest_est:
            est_no = str(latest_est.estimate_no)
            numbers = []
            stri = []
            for word in est_no:
                if word.isdigit():
                    numbers.append(word)
                else:
                    stri.append(word)
            
            num=''
            for i in numbers:
                num +=i
            
            st = ''
            for j in stri:
                st = st+j

            estimate_num = int(num)+1

            if num[0] == '0':
                if estimate_num <10:
                    nxtEST = st+'0'+ str(estimate_num)
                else:
                    nxtEST = st+ str(estimate_num)
            else:
                nxtEST = st+ str(estimate_num)

        context = {
            'allmodules':allmodules, 'com':com, 'cmp':cmp, 'data':data, 'customers':cust, 'items':itms, 'pTerms':trms,'list':lst,
            'ref_no':new_number,'ESTNo':nxtEST,'units':units, 'accounts':acc
        }
        return render(request,'company/Fin_Add_Estimate.html',context)
    else:
       return redirect('/')

def Fin_createEstimate(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        if request.method == 'POST':
            ESTNo = request.POST['estimate_no']

            PatternStr = []
            for word in ESTNo:
                if word.isdigit():
                    pass
                else:
                    PatternStr.append(word)
            
            pattern = ''
            for j in PatternStr:
                pattern += j

            pattern_exists = checkEstimateNumberPattern(pattern)

            if pattern !="" and pattern_exists:
                res = f'<script>alert("Estimate No. Pattern already Exists.! Try another!");window.history.back();</script>'
                return HttpResponse(res)

            if Fin_Estimate.objects.filter(Company = com, estimate_no__iexact = ESTNo).exists():
                res = f'<script>alert("Estimate Number `{ESTNo}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)

            Estimate = Fin_Estimate(
                Company = com,
                LoginDetails = com.Login_Id,
                Customer = None if request.POST['customerId'] == "" else Fin_Customers.objects.get(id = request.POST['customerId']),
                customer_email = request.POST['customerEmail'],
                billing_address = request.POST['bill_address'],
                gst_type = request.POST['gst_type'],
                gstin = request.POST['gstin'],
                place_of_supply = request.POST['place_of_supply'],
                reference_no = request.POST['reference_number'],
                estimate_no = ESTNo,
                payment_terms = Fin_Company_Payment_Terms.objects.get(id = request.POST['payment_term']),
                estimate_date = request.POST['estimate_date'],
                exp_date = datetime.strptime(request.POST['exp_date'], '%d-%m-%Y').date(),
                subtotal = 0.0 if request.POST['subtotal'] == "" else float(request.POST['subtotal']),
                igst = 0.0 if request.POST['igst'] == "" else float(request.POST['igst']),
                cgst = 0.0 if request.POST['cgst'] == "" else float(request.POST['cgst']),
                sgst = 0.0 if request.POST['sgst'] == "" else float(request.POST['sgst']),
                tax_amount = 0.0 if request.POST['taxamount'] == "" else float(request.POST['taxamount']),
                adjustment = 0.0 if request.POST['adj'] == "" else float(request.POST['adj']),
                shipping_charge = 0.0 if request.POST['ship'] == "" else float(request.POST['ship']),
                grandtotal = 0.0 if request.POST['grandtotal'] == "" else float(request.POST['grandtotal']),
                note = request.POST['note']
            )

            Estimate.save()

            if len(request.FILES) != 0:
                Estimate.file=request.FILES.get('file')
            Estimate.save()

            if 'Draft' in request.POST:
                Estimate.status = "Draft"
            elif "Save" in request.POST:
                Estimate.status = "Saved" 
            Estimate.save()

            # Save Estimate items.

            itemId = request.POST.getlist("item_id[]")
            itemName = request.POST.getlist("item_name[]")
            hsn  = request.POST.getlist("hsn[]")
            qty = request.POST.getlist("qty[]")
            price = request.POST.getlist("price[]")
            tax = request.POST.getlist("taxGST[]") if request.POST['place_of_supply'] == com.State else request.POST.getlist("taxIGST[]")
            discount = request.POST.getlist("discount[]")
            total = request.POST.getlist("total[]")

            if len(itemId)==len(itemName)==len(hsn)==len(qty)==len(price)==len(tax)==len(discount)==len(total) and itemId and itemName and hsn and qty and price and tax and discount and total:
                mapped = zip(itemId,itemName,hsn,qty,price,tax,discount,total)
                mapped = list(mapped)
                for ele in mapped:
                    itm = Fin_Items.objects.get(id = int(ele[0]))
                    Fin_Estimate_Items.objects.create(Estimate = Estimate, Item = itm, hsn = ele[2], quantity = int(ele[3]), price = float(ele[4]), tax = ele[5], discount = float(ele[6]), total = float(ele[7]))
                    # itm.current_stock -= int(ele[3])
                    # itm.save()
            
            # Save transaction
                    
            Fin_Estimate_History.objects.create(
                Company = com,
                LoginDetails = data,
                Estimate = Estimate,
                action = 'Created'
            )

            return redirect(Fin_estimates)
        else:
            return redirect(Fin_addEstimate)
    else:
       return redirect('/')

def Fin_viewEstimate(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)

        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            cmp = com
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            cmp = com.company_id
        
        allmodules = Fin_Modules_List.objects.get(company_id = cmp,status = 'New')
        Estimate = Fin_Estimate.objects.get(id = id)
        cmt = Fin_Estimate_Comments.objects.filter(Estimate = Estimate)
        hist = Fin_Estimate_History.objects.filter(Estimate = Estimate).last()
        EstItems = Fin_Estimate_Items.objects.filter(Estimate = Estimate)
        try:
            created = Fin_Estimate_History.objects.get(Estimate = Estimate, action = 'Created')
        except:
            created = None

        return render(request,'company/Fin_View_Estimate.html',{'allmodules':allmodules,'com':com,'cmp':cmp, 'data':data, 'estimate':Estimate,'estItems':EstItems, 'history':hist, 'comments':cmt, 'created':created})
    else:
       return redirect('/')

def Fin_editEstimate(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            cmp = com
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            cmp = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = cmp,status = 'New')
        est = Fin_Estimate.objects.get(id = id)
        estItms = Fin_Estimate_Items.objects.filter(Estimate = est)
        cust = Fin_Customers.objects.filter(Company = cmp, status = 'Active')
        itms = Fin_Items.objects.filter(Company = cmp, status = 'Active')
        trms = Fin_Company_Payment_Terms.objects.filter(Company = cmp)
        bnk = Fin_Banking.objects.filter(company = cmp)
        lst = Fin_Price_List.objects.filter(Company = cmp, status = 'Active')
        units = Fin_Units.objects.filter(Company = cmp)
        acc = Fin_Chart_Of_Account.objects.filter(Q(account_type='Expense') | Q(account_type='Other Expense') | Q(account_type='Cost Of Goods Sold'), Company=cmp).order_by('account_name')

        context = {
            'allmodules':allmodules, 'com':com, 'cmp':cmp, 'data':data,'estimate':est, 'estItems':estItms, 'customers':cust, 'items':itms, 'pTerms':trms,'list':lst,
            'banks':bnk,'units':units, 'accounts':acc
        }
        return render(request,'company/Fin_Edit_Estimate.html',context)
    else:
       return redirect('/')

def Fin_updateEstimate(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        est = Fin_Estimate.objects.get(id = id)
        if request.method == 'POST':
            ESTNo = request.POST['estimate_no']

            PatternStr = []
            for word in ESTNo:
                if word.isdigit():
                    pass
                else:
                    PatternStr.append(word)
            
            pattern = ''
            for j in PatternStr:
                pattern += j

            pattern_exists = checkEstimateNumberPattern(pattern)

            if pattern !="" and pattern_exists:
                res = f'<script>alert("Estimate No. Pattern already Exists.! Try another!");window.history.back();</script>'
                return HttpResponse(res)

            if est.estimate_no != ESTNo and Fin_Estimate.objects.filter(Company = com, estimate_no__iexact = ESTNo).exists():
                res = f'<script>alert("Estimate Number `{ESTNo}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)

            est.Customer = None if request.POST['customerId'] == "" else Fin_Customers.objects.get(id = request.POST['customerId'])
            est.customer_email = request.POST['customerEmail']
            est.billing_address = request.POST['bill_address']
            est.gst_type = request.POST['gst_type']
            est.gstin = request.POST['gstin']
            est.place_of_supply = request.POST['place_of_supply']

            est.estimate_no = ESTNo
            est.payment_terms = Fin_Company_Payment_Terms.objects.get(id = request.POST['payment_term'])
            est.estimate_date = request.POST['estimate_date']
            est.exp_date = datetime.strptime(request.POST['exp_date'], '%d-%m-%Y').date()

            est.subtotal = 0.0 if request.POST['subtotal'] == "" else float(request.POST['subtotal'])
            est.igst = 0.0 if request.POST['igst'] == "" else float(request.POST['igst'])
            est.cgst = 0.0 if request.POST['cgst'] == "" else float(request.POST['cgst'])
            est.sgst = 0.0 if request.POST['sgst'] == "" else float(request.POST['sgst'])
            est.tax_amount = 0.0 if request.POST['taxamount'] == "" else float(request.POST['taxamount'])
            est.adjustment = 0.0 if request.POST['adj'] == "" else float(request.POST['adj'])
            est.shipping_charge = 0.0 if request.POST['ship'] == "" else float(request.POST['ship'])
            est.grandtotal = 0.0 if request.POST['grandtotal'] == "" else float(request.POST['grandtotal'])

            est.note = request.POST['note']

            if len(request.FILES) != 0:
                est.file=request.FILES.get('file')

            est.save()

            # Save estimate items.

            itemId = request.POST.getlist("item_id[]")
            itemName = request.POST.getlist("item_name[]")
            hsn  = request.POST.getlist("hsn[]")
            qty = request.POST.getlist("qty[]")
            price = request.POST.getlist("price[]")
            tax = request.POST.getlist("taxGST[]") if request.POST['place_of_supply'] == com.State else request.POST.getlist("taxIGST[]")
            discount = request.POST.getlist("discount[]")
            total = request.POST.getlist("total[]")
            est_item_ids = request.POST.getlist("id[]")
            EstItem_ids = [int(id) for id in est_item_ids]

            estimate_items = Fin_Estimate_Items.objects.filter(Estimate = est)
            object_ids = [obj.id for obj in estimate_items]

            ids_to_delete = [obj_id for obj_id in object_ids if obj_id not in EstItem_ids]

            Fin_Estimate_Items.objects.filter(id__in=ids_to_delete).delete()
            
            count = Fin_Estimate_Items.objects.filter(Estimate = est).count()

            if len(itemId)==len(itemName)==len(hsn)==len(qty)==len(price)==len(tax)==len(discount)==len(total)==len(EstItem_ids) and EstItem_ids and itemId and itemName and hsn and qty and price and tax and discount and total:
                mapped = zip(itemId,itemName,hsn,qty,price,tax,discount,total,EstItem_ids)
                mapped = list(mapped)
                for ele in mapped:
                    if int(len(itemId))>int(count):
                        if ele[8] == 0:
                            itm = Fin_Items.objects.get(id = int(ele[0]))
                            Fin_Estimate_Items.objects.create(Estimate = est, Item = itm, hsn = ele[2], quantity = int(ele[3]), price = float(ele[4]), tax = ele[5], discount = float(ele[6]), total = float(ele[7]))
                        else:
                            itm = Fin_Items.objects.get(id = int(ele[0]))
                            Fin_Estimate_Items.objects.filter( id = int(ele[8])).update(Estimate = est, Item = itm, hsn = ele[2], quantity = int(ele[3]), price = float(ele[4]), tax = ele[5], discount = float(ele[6]), total = float(ele[7]))
                    else:
                        itm = Fin_Items.objects.get(id = int(ele[0]))
                        Fin_Estimate_Items.objects.filter( id = int(ele[8])).update(Estimate = est, Item = itm, hsn = ele[2], quantity = int(ele[3]), price = float(ele[4]), tax = ele[5], discount = float(ele[6]), total = float(ele[7]))
            
            # Save transaction
                    
            Fin_Estimate_History.objects.create(
                Company = com,
                LoginDetails = data,
                Estimate = est,
                action = 'Edited'
            )

            return redirect(Fin_viewEstimate, id)
        else:
            return redirect(Fin_editEstimate, id)
    else:
       return redirect('/')
    
def Fin_convertEstimate(request,id):
    if 's_id' in request.session:

        est = Fin_Estimate.objects.get(id = id)
        est.status = 'Saved'
        est.save()
        return redirect(Fin_viewEstimate, id)

def Fin_addEstimateComment(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        est = Fin_Estimate.objects.get(id = id)
        if request.method == "POST":
            cmt = request.POST['comment'].strip()

            Fin_Estimate_Comments.objects.create(Company = com, Estimate = est, comments = cmt)
            return redirect(Fin_viewEstimate, id)
        return redirect(Fin_viewEstimate, id)
    return redirect('/')

def Fin_deleteEstimateComment(request,id):
    if 's_id' in request.session:
        cmt = Fin_Estimate_Comments.objects.get(id = id)
        estId = cmt.Estimate.id
        cmt.delete()
        return redirect(Fin_viewEstimate, estId)
    
def Fin_estimateHistory(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)

        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            cmp = com
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            cmp = com.company_id
        
        allmodules = Fin_Modules_List.objects.get(company_id = cmp,status = 'New')
        est = Fin_Estimate.objects.get(id = id)
        his = Fin_Estimate_History.objects.filter(Estimate = est)

        return render(request,'company/Fin_Estimate_History.html',{'allmodules':allmodules,'com':com,'data':data,'history':his, 'estimate':est})
    else:
       return redirect('/')
    
def Fin_deleteEstimate(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        est = Fin_Estimate.objects.get( id = id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        Fin_Estimate_Items.objects.filter(Estimate = est).delete()

        # Storing ref number to deleted table
        # if entry exists and lesser than the current, update and save => Only one entry per company
        if Fin_Estimate_Reference.objects.filter(Company = com).exists():
            deleted = Fin_Estimate_Reference.objects.get(Company = com)
            if int(est.reference_no) > int(deleted.reference_no):
                deleted.reference_no = est.reference_no
                deleted.save()
        else:
            Fin_Estimate_Reference.objects.create(Company = com, reference_no = est.reference_no)
        
        est.delete()
        return redirect(Fin_estimates)

def Fin_estimatePdf(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        est = Fin_Estimate.objects.get(id = id)
        itms = Fin_Estimate_Items.objects.filter(Estimate = est)
    
        context = {'estimate':est, 'estItems':itms,'cmp':com}
        
        template_path = 'company/Fin_Estimate_Pdf.html'
        fname = 'Estimate_' + est.estimate_no

        # Create a Django response object, and specify content_type as pdftemp_
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] =f'attachment; filename = {fname}.pdf'
        # find the template and render it.
        template = get_template(template_path)
        html = template.render(context)

        # create a pdf
        pisa_status = pisa.CreatePDF(
        html, dest=response)
        # if error then show some funny view
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
    else:
        return redirect('/')

def Fin_shareEstimateToEmail(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        est = Fin_Estimate.objects.get(id = id)
        itms = Fin_Estimate_Items.objects.filter(Estimate = est)
        try:
            if request.method == 'POST':
                emails_string = request.POST['email_ids']

                # Split the string by commas and remove any leading or trailing whitespace
                emails_list = [email.strip() for email in emails_string.split(',')]
                email_message = request.POST['email_message']
                # print(emails_list)
            
                context = {'estimate':est, 'estItems':itms,'cmp':com}
                template_path = 'company/Fin_Estimate_Pdf.html'
                template = get_template(template_path)

                html  = template.render(context)
                result = BytesIO()
                pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
                pdf = result.getvalue()
                filename = f'Estimate_{est.estimate_no}'
                subject = f"Estimate_{est.estimate_no}"
                email = EmailMessage(subject, f"Hi,\nPlease find the attached Estimate for - #-{est.estimate_no}. \n{email_message}\n\n--\nRegards,\n{com.Company_name}\n{com.Address}\n{com.State} - {com.Country}\n{com.Contact}", from_email=settings.EMAIL_HOST_USER, to=emails_list)
                email.attach(filename, pdf, "application/pdf")
                email.send(fail_silently=False)

                messages.success(request, 'Estimate details has been shared via email successfully..!')
                return redirect(Fin_viewEstimate,id)
        except Exception as e:
            print(e)
            messages.error(request, f'{e}')
            return redirect(Fin_viewEstimate, id)

def Fin_attachEstimateFile(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        est = Fin_Estimate.objects.get(id = id)

        if request.method == 'POST' and len(request.FILES) != 0:
            est.file = request.FILES.get('file')
            est.save()

        return redirect(Fin_viewEstimate, id)
    else:
        return redirect('/')

def Fin_convertEstimateToInvoice(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            cmp = com
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            cmp = com.company_id

        est = Fin_Estimate.objects.get(id = id)
        estItms = Fin_Estimate_Items.objects.filter(Estimate = est)
        cust = Fin_Customers.objects.filter(Company = cmp, status = 'Active')
        itms = Fin_Items.objects.filter(Company = cmp, status = 'Active')
        trms = Fin_Company_Payment_Terms.objects.filter(Company = cmp)
        bnk = Fin_Banking.objects.filter(company = cmp)
        lst = Fin_Price_List.objects.filter(Company = cmp, status = 'Active')
        units = Fin_Units.objects.filter(Company = cmp)
        acc = Fin_Chart_Of_Account.objects.filter(Q(account_type='Expense') | Q(account_type='Other Expense') | Q(account_type='Cost Of Goods Sold'), Company=cmp).order_by('account_name')

        # Fetching last invoice and assigning upcoming ref no as current + 1
        # Also check for if any bill is deleted and ref no is continuos w r t the deleted invoice
        latest_inv = Fin_Invoice.objects.filter(Company = cmp).order_by('-id').first()

        new_number = int(latest_inv.reference_no) + 1 if latest_inv else 1

        if Fin_Invoice_Reference.objects.filter(Company = cmp).exists():
            deleted = Fin_Invoice_Reference.objects.get(Company = cmp)
            
            if deleted:
                while int(deleted.reference_no) >= new_number:
                    new_number+=1

        # Finding next invoice number w r t last invoic number if exists.
        nxtInv = ""
        lastInv = Fin_Invoice.objects.filter(Company = cmp).last()
        if lastInv:
            inv_no = str(lastInv.invoice_no)
            numbers = []
            stri = []
            for word in inv_no:
                if word.isdigit():
                    numbers.append(word)
                else:
                    stri.append(word)
            
            num=''
            for i in numbers:
                num +=i
            
            st = ''
            for j in stri:
                st = st+j

            inv_num = int(num)+1

            if num[0] == '0':
                if inv_num <10:
                    nxtInv = st+'0'+ str(inv_num)
                else:
                    nxtInv = st+ str(inv_num)
            else:
                nxtInv = st+ str(inv_num)

        context = {
            'allmodules':allmodules, 'com':com, 'cmp':cmp, 'data':data,'estimate':est, 'estItems':estItms, 'customers':cust, 'items':itms, 'pTerms':trms,'list':lst,
            'banks':bnk,'units':units, 'accounts':acc,'ref_no':new_number,'invNo':nxtInv
        }
        return render(request,'company/Fin_Convert_Estimate_toInvoice.html',context)
    else:
       return redirect('/')

def Fin_estimateConvertInvoice(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        est = Fin_Estimate.objects.get(id = id)
        if request.method == 'POST':
            invNum = request.POST['invoice_no']
            if Fin_Invoice.objects.filter(Company = com, invoice_no__iexact = invNum).exists():
                res = f'<script>alert("Invoice Number `{invNum}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)

            inv = Fin_Invoice(
                Company = com,
                LoginDetails = com.Login_Id,
                Customer = Fin_Customers.objects.get(id = request.POST['customer']),
                customer_email = request.POST['customerEmail'],
                billing_address = request.POST['bill_address'],
                gst_type = request.POST['gst_type'],
                gstin = request.POST['gstin'],
                place_of_supply = request.POST['place_of_supply'],
                reference_no = request.POST['reference_number'],
                invoice_no = invNum,
                payment_terms = Fin_Company_Payment_Terms.objects.get(id = request.POST['payment_term']),
                invoice_date = request.POST['invoice_date'],
                duedate = datetime.strptime(request.POST['due_date'], '%d-%m-%Y').date(),
                salesOrder_no = request.POST['order_number'],
                exp_ship_date = datetime.strptime(request.POST['due_date'], '%d-%m-%Y').date(),
                price_list_applied = True if 'priceList' in request.POST else False,
                payment_method = None if request.POST['payment_method'] == "" else request.POST['payment_method'],
                cheque_no = None if request.POST['cheque_id'] == "" else request.POST['cheque_id'],
                upi_no = None if request.POST['upi_id'] == "" else request.POST['upi_id'],
                bank_acc_no = None if request.POST['bnk_id'] == "" else request.POST['bnk_id'],
                subtotal = 0.0 if request.POST['subtotal'] == "" else float(request.POST['subtotal']),
                igst = 0.0 if request.POST['igst'] == "" else float(request.POST['igst']),
                cgst = 0.0 if request.POST['cgst'] == "" else float(request.POST['cgst']),
                sgst = 0.0 if request.POST['sgst'] == "" else float(request.POST['sgst']),
                tax_amount = 0.0 if request.POST['taxamount'] == "" else float(request.POST['taxamount']),
                adjustment = 0.0 if request.POST['adj'] == "" else float(request.POST['adj']),
                shipping_charge = 0.0 if request.POST['ship'] == "" else float(request.POST['ship']),
                grandtotal = 0.0 if request.POST['grandtotal'] == "" else float(request.POST['grandtotal']),
                paid_off = 0.0 if request.POST['advance'] == "" else float(request.POST['advance']),
                balance = request.POST['grandtotal'] if request.POST['balance'] == "" else float(request.POST['balance']),
                note = request.POST['note'],
                status = "Saved" 
            )

            inv.save()

            if len(request.FILES) != 0:
                inv.file=request.FILES.get('file')
            inv.save()

            # Save invoice items.

            itemId = request.POST.getlist("item_id[]")
            itemName = request.POST.getlist("item_name[]")
            hsn  = request.POST.getlist("hsn[]")
            qty = request.POST.getlist("qty[]")
            price = request.POST.getlist("priceListPrice[]") if 'priceList' in request.POST else request.POST.getlist("price[]")
            tax = request.POST.getlist("taxGST[]") if request.POST['place_of_supply'] == com.State else request.POST.getlist("taxIGST[]")
            discount = request.POST.getlist("discount[]")
            total = request.POST.getlist("total[]")

            if len(itemId)==len(itemName)==len(hsn)==len(qty)==len(price)==len(tax)==len(discount)==len(total) and itemId and itemName and hsn and qty and price and tax and discount and total:
                mapped = zip(itemId,itemName,hsn,qty,price,tax,discount,total)
                mapped = list(mapped)
                for ele in mapped:
                    itm = Fin_Items.objects.get(id = int(ele[0]))
                    Fin_Invoice_Items.objects.create(Invoice = inv, Item = itm, hsn = ele[2], quantity = int(ele[3]), price = float(ele[4]), tax = ele[5], discount = float(ele[6]), total = float(ele[7]))
                    itm.current_stock -= int(ele[3])
                    itm.save()
            
            # Save transaction
                    
            Fin_Invoice_History.objects.create(
                Company = com,
                LoginDetails = data,
                Invoice = inv,
                action = 'Created'
            )

            # Save invoice and balance details to Estimate

            est.converted_to_invoice = inv
            est.balance = float(inv.balance)
            est.save()

            return redirect(Fin_estimates)
        else:
            return redirect(Fin_convertEstimateToInvoice, id)
    else:
       return redirect('/')

def Fin_convertEstimateToSalesOrder(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            cmp = com
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            cmp = com.company_id
        
        est = Fin_Estimate.objects.get(id = id)
        estitms = Fin_Estimate_Items.objects.filter(Estimate = est)
        allmodules = Fin_Modules_List.objects.get(company_id = cmp,status = 'New')
        cust = Fin_Customers.objects.filter(Company = cmp, status = 'Active')
        itms = Fin_Items.objects.filter(Company = cmp, status = 'Active')
        trms = Fin_Company_Payment_Terms.objects.filter(Company = cmp)
        bnk = Fin_Banking.objects.filter(company = cmp)
        lst = Fin_Price_List.objects.filter(Company = cmp, status = 'Active')
        units = Fin_Units.objects.filter(Company = cmp)
        acc = Fin_Chart_Of_Account.objects.filter(Q(account_type='Expense') | Q(account_type='Other Expense') | Q(account_type='Cost Of Goods Sold'), Company=cmp).order_by('account_name')

        # Fetching last sales order and assigning upcoming ref no as current + 1
        # Also check for if any bill is deleted and ref no is continuos w r t the deleted sales order
        latest_so = Fin_Sales_Order.objects.filter(Company = cmp).order_by('-id').first()

        new_number = int(latest_so.reference_no) + 1 if latest_so else 1

        if Fin_Sales_Order_Reference.objects.filter(Company = cmp).exists():
            deleted = Fin_Sales_Order_Reference.objects.get(Company = cmp)
            
            if deleted:
                while int(deleted.reference_no) >= new_number:
                    new_number+=1

        # Finding next SO number w r t last SO number if exists.
        nxtSO = ""
        lastSO = Fin_Sales_Order.objects.filter(Company = cmp).last()
        if lastSO:
            salesOrder_no = str(lastSO.sales_order_no)
            numbers = []
            stri = []
            for word in salesOrder_no:
                if word.isdigit():
                    numbers.append(word)
                else:
                    stri.append(word)
            
            num=''
            for i in numbers:
                num +=i
            
            st = ''
            for j in stri:
                st = st+j

            s_order_num = int(num)+1

            if num[0] == '0':
                if s_order_num <10:
                    nxtSO = st+'0'+ str(s_order_num)
                else:
                    nxtSO = st+ str(s_order_num)
            else:
                nxtSO = st+ str(s_order_num)

        context = {
            'allmodules':allmodules, 'com':com, 'cmp':cmp, 'data':data, 'customers':cust, 'items':itms, 'pTerms':trms,'list':lst,
            'ref_no':new_number,'banks':bnk,'SONo':nxtSO,'units':units, 'accounts':acc, 'estimate':est, 'estItems':estitms,
        }
        return render(request,'company/Fin_Convert_Estimate_toSalesOrder.html',context)
    else:
       return redirect('/')

def Fin_estimateConvertSalesOrder(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        est = Fin_Estimate.objects.get(id = id)
        if request.method == 'POST':
            SONum = request.POST['sales_order_no']
            if Fin_Sales_Order.objects.filter(Company = com, sales_order_no__iexact = SONum).exists():
                res = f'<script>alert("Sales Order Number `{SONum}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)

            SOrder = Fin_Sales_Order(
                Company = com,
                LoginDetails = com.Login_Id,
                Customer = None if request.POST['customerId'] == "" else Fin_Customers.objects.get(id = request.POST['customerId']),
                customer_email = request.POST['customerEmail'],
                billing_address = request.POST['bill_address'],
                gst_type = request.POST['gst_type'],
                gstin = request.POST['gstin'],
                place_of_supply = request.POST['place_of_supply'],
                reference_no = request.POST['reference_number'],
                sales_order_no = SONum,
                payment_terms = Fin_Company_Payment_Terms.objects.get(id = request.POST['payment_term']),
                sales_order_date = request.POST['sales_order_date'],
                exp_ship_date = datetime.strptime(request.POST['shipment_date'], '%d-%m-%Y').date(),
                payment_method = None if request.POST['payment_method'] == "" else request.POST['payment_method'],
                cheque_no = None if request.POST['cheque_id'] == "" else request.POST['cheque_id'],
                upi_no = None if request.POST['upi_id'] == "" else request.POST['upi_id'],
                bank_acc_no = None if request.POST['bnk_id'] == "" else request.POST['bnk_id'],
                subtotal = 0.0 if request.POST['subtotal'] == "" else float(request.POST['subtotal']),
                igst = 0.0 if request.POST['igst'] == "" else float(request.POST['igst']),
                cgst = 0.0 if request.POST['cgst'] == "" else float(request.POST['cgst']),
                sgst = 0.0 if request.POST['sgst'] == "" else float(request.POST['sgst']),
                tax_amount = 0.0 if request.POST['taxamount'] == "" else float(request.POST['taxamount']),
                adjustment = 0.0 if request.POST['adj'] == "" else float(request.POST['adj']),
                shipping_charge = 0.0 if request.POST['ship'] == "" else float(request.POST['ship']),
                grandtotal = 0.0 if request.POST['grandtotal'] == "" else float(request.POST['grandtotal']),
                paid_off = 0.0 if request.POST['advance'] == "" else float(request.POST['advance']),
                balance = request.POST['grandtotal'] if request.POST['balance'] == "" else float(request.POST['balance']),
                note = request.POST['note']
            )

            SOrder.save()

            if len(request.FILES) != 0:
                SOrder.file=request.FILES.get('file')
            SOrder.save()

            if 'Draft' in request.POST:
                SOrder.status = "Draft"
            elif "Save" in request.POST:
                SOrder.status = "Saved" 
            SOrder.save()

            # Save Sales Order items.

            itemId = request.POST.getlist("item_id[]")
            itemName = request.POST.getlist("item_name[]")
            hsn  = request.POST.getlist("hsn[]")
            qty = request.POST.getlist("qty[]")
            price = request.POST.getlist("price[]")
            tax = request.POST.getlist("taxGST[]") if request.POST['place_of_supply'] == com.State else request.POST.getlist("taxIGST[]")
            discount = request.POST.getlist("discount[]")
            total = request.POST.getlist("total[]")

            if len(itemId)==len(itemName)==len(hsn)==len(qty)==len(price)==len(tax)==len(discount)==len(total) and itemId and itemName and hsn and qty and price and tax and discount and total:
                mapped = zip(itemId,itemName,hsn,qty,price,tax,discount,total)
                mapped = list(mapped)
                for ele in mapped:
                    itm = Fin_Items.objects.get(id = int(ele[0]))
                    Fin_Sales_Order_Items.objects.create(SalesOrder = SOrder, Item = itm, hsn = ele[2], quantity = int(ele[3]), price = float(ele[4]), tax = ele[5], discount = float(ele[6]), total = float(ele[7]))
                    # itm.current_stock -= int(ele[3])
                    # itm.save()
            
            # Save transaction
                    
            Fin_Sales_Order_History.objects.create(
                Company = com,
                LoginDetails = data,
                SalesOrder = SOrder,
                action = 'Created'
            )

            # Save sales order details to Estimate and update Estimate Balance

            est.converted_to_sales_order = SOrder
            est.balance = float(SOrder.balance)
            est.save()

            return redirect(Fin_estimates)
        else:
            return redirect(Fin_convertEstimateToSalesOrder, id)
    else:
       return redirect('/')

def Fin_checkEstimateNumber(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        EstNo = request.GET['EstNum']

        nxtEstNo = ""
        lastEstmate = Fin_Estimate.objects.filter(Company = com).last()
        if lastEstmate:
            Est_no = str(lastEstmate.estimate_no)
            numbers = []
            stri = []
            for word in Est_no:
                if word.isdigit():
                    numbers.append(word)
                else:
                    stri.append(word)
            
            num=''
            for i in numbers:
                num +=i
            
            st = ''
            for j in stri:
                st = st+j

            est_num = int(num)+1

            if num[0] == '0':
                if est_num <10:
                    nxtEstNo = st+'0'+ str(est_num)
                else:
                    nxtEstNo = st+ str(est_num)
            else:
                nxtEstNo = st+ str(est_num)

        PatternStr = []
        for word in EstNo:
            if word.isdigit():
                pass
            else:
                PatternStr.append(word)
        
        pattern = ''
        for j in PatternStr:
            pattern += j

        pattern_exists = checkEstimateNumberPattern(pattern)

        if pattern !="" and pattern_exists:
            return JsonResponse({'status':False, 'message':'Estimate No. Pattern already Exists.!'})
        elif Fin_Estimate.objects.filter(Company = com, estimate_no__iexact = EstNo).exists():
            return JsonResponse({'status':False, 'message':'Estimate No. already Exists.!'})
        elif nxtEstNo != "" and EstNo != nxtEstNo:
            return JsonResponse({'status':False, 'message':'Estimate No. is not continuous.!'})
        else:
            return JsonResponse({'status':True, 'message':'Number is okay.!'})
    else:
       return redirect('/')

def checkEstimateNumberPattern(pattern):
    models = [Fin_Invoice, Fin_Sales_Order, Fin_Recurring_Invoice, Fin_Purchase_Bill, Fin_Manual_Journal]

    for model in models:
        field_name = model.getNumFieldName(model)
        if model.objects.filter(**{f"{field_name}__icontains": pattern}).exists():
            return True
    return False
    
def Fin_convertEstimateToRecurringInvoice(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            cmp = com
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            cmp = com.company_id

        est = Fin_Estimate.objects.get(id = id)
        estItms = Fin_Estimate_Items.objects.filter(Estimate = est)
        cust = Fin_Customers.objects.filter(Company = cmp, status = 'Active')
        itms = Fin_Items.objects.filter(Company = cmp, status = 'Active')
        trms = Fin_Company_Payment_Terms.objects.filter(Company = cmp)
        bnk = Fin_Banking.objects.filter(company = cmp)
        lst = Fin_Price_List.objects.filter(Company = cmp, status = 'Active')
        units = Fin_Units.objects.filter(Company = cmp)
        acc = Fin_Chart_Of_Account.objects.filter(Q(account_type='Expense') | Q(account_type='Other Expense') | Q(account_type='Cost Of Goods Sold'), Company=cmp).order_by('account_name')
        repeat = Fin_CompanyRepeatEvery.objects.filter(company = cmp)
        priceList = Fin_Price_List.objects.filter(Company = cmp, type = 'Sales', status = 'Active')

        # Fetching last invoice and assigning upcoming ref no as current + 1
        # Also check for if any bill is deleted and ref no is continuos w r t the deleted invoice
        latest_inv = Fin_Recurring_Invoice.objects.filter(Company = cmp).order_by('-id').first()

        new_number = int(latest_inv.reference_no) + 1 if latest_inv else 1

        if Fin_Recurring_Invoice_Reference.objects.filter(Company = cmp).exists():
            deleted = Fin_Recurring_Invoice_Reference.objects.get(Company = cmp)
            
            if deleted:
                while int(deleted.reference_no) >= new_number:
                    new_number+=1

        # Finding next rec_invoice number w r t last rec_invoice number if exists.
        nxtInv = ""
        lastInv = Fin_Recurring_Invoice.objects.filter(Company = cmp).last()
        if lastInv:
            inv_no = str(lastInv.rec_invoice_no)
            numbers = []
            stri = []
            for word in inv_no:
                if word.isdigit():
                    numbers.append(word)
                else:
                    stri.append(word)
            
            num=''
            for i in numbers:
                num +=i
            
            st = ''
            for j in stri:
                st = st+j

            inv_num = int(num)+1

            if num[0] == '0':
                if inv_num <10:
                    nxtInv = st+'0'+ str(inv_num)
                else:
                    nxtInv = st+ str(inv_num)
            else:
                nxtInv = st+ str(inv_num)
        else:
            nxtInv = 'RI01'

        context = {
            'allmodules':allmodules, 'com':com, 'cmp':cmp, 'data':data,'estimate':est, 'estItems':estItms, 'customers':cust, 'items':itms, 'pTerms':trms,'list':lst,
            'banks':bnk,'units':units, 'accounts':acc,'ref_no':new_number,'invNo':nxtInv, 'priceListItems':priceList, 'repeat':repeat,
        }
        return render(request,'company/Fin_Convert_Estimate_toRecInvoice.html',context)
    else:
       return redirect('/')   
       
def Fin_estimateConvertRecInvoice(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        est = Fin_Estimate.objects.get(id = id)

        if request.method == 'POST':
            invNum = request.POST['rec_invoice_no']
            if Fin_Recurring_Invoice.objects.filter(Company = com, rec_invoice_no__iexact = invNum).exists():
                res = f'<script>alert("Rec. Invoice Number `{invNum}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)

            inv = Fin_Recurring_Invoice(
                Company = com,
                LoginDetails = com.Login_Id,
                Customer = Fin_Customers.objects.get(id = request.POST['customerId']),
                customer_email = request.POST['customerEmail'],
                billing_address = request.POST['bill_address'],
                gst_type = request.POST['gst_type'],
                gstin = request.POST['gstin'],
                place_of_supply = request.POST['place_of_supply'],
                profile_name = request.POST['profile_name'],
                entry_type = None if request.POST['entry_type'] == "" else request.POST['entry_type'],
                reference_no = request.POST['reference_number'],
                rec_invoice_no = invNum,
                payment_terms = Fin_Company_Payment_Terms.objects.get(id = request.POST['payment_term']),
                start_date = request.POST['start_date'],
                end_date = datetime.strptime(request.POST['end_date'], '%d-%m-%Y').date(),
                salesOrder_no = request.POST['order_number'],
                price_list_applied = True if 'priceList' in request.POST else False,
                price_list = None if request.POST['price_list_id'] == "" else Fin_Price_List.objects.get(id = request.POST['price_list_id']),
                repeat_every = Fin_CompanyRepeatEvery.objects.get(id = request.POST['repeat_every']),
                payment_method = None if request.POST['payment_method'] == "" else request.POST['payment_method'],
                cheque_no = None if request.POST['cheque_id'] == "" else request.POST['cheque_id'],
                upi_no = None if request.POST['upi_id'] == "" else request.POST['upi_id'],
                bank_acc_no = None if request.POST['bnk_id'] == "" else request.POST['bnk_id'],
                subtotal = 0.0 if request.POST['subtotal'] == "" else float(request.POST['subtotal']),
                igst = 0.0 if request.POST['igst'] == "" else float(request.POST['igst']),
                cgst = 0.0 if request.POST['cgst'] == "" else float(request.POST['cgst']),
                sgst = 0.0 if request.POST['sgst'] == "" else float(request.POST['sgst']),
                tax_amount = 0.0 if request.POST['taxamount'] == "" else float(request.POST['taxamount']),
                adjustment = 0.0 if request.POST['adj'] == "" else float(request.POST['adj']),
                shipping_charge = 0.0 if request.POST['ship'] == "" else float(request.POST['ship']),
                grandtotal = 0.0 if request.POST['grandtotal'] == "" else float(request.POST['grandtotal']),
                paid_off = 0.0 if request.POST['advance'] == "" else float(request.POST['advance']),
                balance = request.POST['grandtotal'] if request.POST['balance'] == "" else float(request.POST['balance']),
                note = request.POST['note']
            )

            inv.save()

            if len(request.FILES) != 0:
                inv.file=request.FILES.get('file')
            inv.save()

            if 'Draft' in request.POST:
                inv.status = "Draft"
            elif "Save" in request.POST:
                inv.status = "Saved" 
            inv.save()

            # Save rec_invoice items.

            itemId = request.POST.getlist("item_id[]")
            itemName = request.POST.getlist("item_name[]")
            hsn  = request.POST.getlist("hsn[]")
            qty = request.POST.getlist("qty[]")
            price = request.POST.getlist("priceListPrice[]") if 'priceList' in request.POST else request.POST.getlist("price[]")
            tax = request.POST.getlist("taxGST[]") if request.POST['place_of_supply'] == com.State else request.POST.getlist("taxIGST[]")
            discount = request.POST.getlist("discount[]")
            total = request.POST.getlist("total[]")

            if len(itemId)==len(itemName)==len(hsn)==len(qty)==len(price)==len(tax)==len(discount)==len(total) and itemId and itemName and hsn and qty and price and tax and discount and total:
                mapped = zip(itemId,itemName,hsn,qty,price,tax,discount,total)
                mapped = list(mapped)
                for ele in mapped:
                    itm = Fin_Items.objects.get(id = int(ele[0]))
                    Fin_Recurring_Invoice_Items.objects.create(RecInvoice = inv, Item = itm, hsn = ele[2], quantity = int(ele[3]), price = float(ele[4]), tax = ele[5], discount = float(ele[6]), total = float(ele[7]))
                    itm.current_stock -= int(ele[3])
                    itm.save()
            
            # Save transaction
                    
            Fin_Recurring_Invoice_History.objects.create(
                Company = com,
                LoginDetails = data,
                RecInvoice = inv,
                action = 'Created'
            )

            # Save sales order details to Estimate and update Estimate Balance

            est.converted_to_rec_invoice = inv
            est.balance = float(inv.balance)
            est.save()

            return redirect(Fin_estimates)
        else:
            return redirect(Fin_convertEstimateToRecurringInvoice, id)
    else:
       return redirect('/')
#End

def Fin_Check_New_Unit(request):
    s_id = request.session['s_id']
    data = Fin_Login_Details.objects.get(id = s_id)
    if data.User_Type == "Company":
        com = Fin_Company_Details.objects.get(Login_Id = s_id)
    else:
        com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
    name = str(request.GET.get('unit_name')).upper()
    if Fin_Units.objects.filter(Company = com, name = name).exists():
        return JsonResponse({'is_exist':True, 'message':'Already Present !!!'})
    return JsonResponse({'is_exist':False})

def Fin_New_Unit(request):
    s_id = request.session['s_id']
    data = Fin_Login_Details.objects.get(id = s_id)
    if data.User_Type == "Company":
        com = Fin_Company_Details.objects.get(Login_Id = s_id)
    else:
        com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
    name = str(request.GET.get('unit_name')).upper()
    if Fin_Units.objects.filter(Company = com, name = name).exists():
        return JsonResponse({'message': 'Error'})
    Fin_Units.objects.create(Company = com, name = name)
    return JsonResponse({'message': 'Success'})



def Fin_Check_New_Term(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        name = request.GET.get('name')
        days = request.GET.get('days')

        if Fin_Company_Payment_Terms.objects.filter(Company = com, term_name__iexact = name).exists():
            msg = f'{name} already exists, Try another.!'
            return JsonResponse({'name_is_exist':True, 'message':msg})
        else:
            if Fin_Company_Payment_Terms.objects.filter(Company = com, days__iexact = days).exists():
                msg = f'{days} already exists, Try another.!'
                return JsonResponse({'name_is_exist':False, 'days_is_exist':True, 'message':msg})
            return JsonResponse({'name_is_exist':False, 'days_is_exist':False})

def Fin_Share_Purchase_Bill(request,id):
    if request.user:
        try:
            if request.method == 'POST':
                emails_string = request.POST['email_ids']

                emails_list = [email.strip() for email in emails_string.split(',')]
                email_message = request.POST['email_message']

                s_id = request.session['s_id']
                data = Fin_Login_Details.objects.get(id = s_id)
                if data.User_Type == "Company":
                    com = Fin_Company_Details.objects.get(Login_Id = s_id)
                else:
                    com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

                pbill = Fin_Purchase_Bill.objects.get(id = id)
                itms = Fin_Purchase_Bill_Item.objects.filter(pbill = pbill)
            
                context = {'pbill': pbill, 'itms':itms, }
                template_path = 'company/Fin_Pbill_Pdf.html'
                template = get_template(template_path)

                html  = template.render(context)
                result = BytesIO()
                pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)#, link_callback=fetch_resources)
                pdf = result.getvalue()
                filename = f'Sales Bill - {pbill.bill_no}.pdf'
                subject = f"SALES BILL - {pbill.bill_no}"
                email = EmailMessage(subject, f"Hi,\nPlease find the attached SALES BILL - Bill-{pbill.bill_no}. \n{email_message}\n\n--\nRegards,\n{com.Company_name}\n{com.Address}\n{com.State} - {com.Country}\n{com.Contact}", from_email=settings.EMAIL_HOST_USER, to=emails_list)
                email.attach(filename, pdf, "application/pdf")
                email.send(fail_silently=False)

                messages.success(request, 'Bill has been shared via email successfully..!')
                return redirect(Fin_View_Purchase_Bill)
        except Exception as e:
            messages.error(request, f'{e}')
            return redirect(Fin_View_Purchase_Bill)
            
            
def Fin_New_Account(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        if request.method == 'GET':
            name = request.GET.get('account_name')
            type = request.GET.get('account_type')
            subAcc = True if 'subAccountCheckBox' in request.POST else False
            parentAcc = request.GET.get('parent_account') if 'subAccountCheckBox' in request.POST else None
            accCode = request.GET.get('account_code')
            bankAccNum = None if request.GET.get('account_number') == "" else request.GET.get('account_number')
            desc = request.GET.get('description')
            
            createdDate = date.today()
            
            #save account and transaction if account doesn't exists already
            if Fin_Chart_Of_Account.objects.filter(Company=com, account_name__iexact=name).exists():
                res = f'<script>alert("{name} already exists, try another!");window.history.back();</script>'
                return JsonResponse({'status':False,'message':res})
            else:
                account = Fin_Chart_Of_Account(
                    Company = com,
                    LoginDetails = data,
                    account_type = type,
                    account_name = name,
                    account_code = accCode,
                    description = desc,
                    balance = 0.0,
                    balance_type = None,
                    credit_card_no = None,
                    sub_account = subAcc,
                    parent_account = parentAcc,
                    bank_account_no = bankAccNum,
                    date = createdDate,
                    create_status = 'added',
                    status = 'active'
                )
                account.save()

                #save transaction

                Fin_ChartOfAccount_History.objects.create(
                    Company = com,
                    LoginDetails = data,
                    account = account,
                    action = 'Created'
                )
                
                return JsonResponse({'status':True})
                
                
#------------- company-------------------
def company_gsttype_change(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        com = Fin_Company_Details.objects.get(Login_Id = s_id)

    
        if request.method == 'POST':
            # Get data from the form
            
            # gstno = request.POST.get('gstno')
            gsttype = request.POST.get('gsttype')

            com.GST_Type = gsttype

            com.save()

            # Check if gsttype is one of the specified values
            if gsttype in ['unregistered Business', 'Overseas', 'Consumer']:
                messages.success(request,'GST Type changed')
                com.GST_NO=''
                com.save()
            else:
                messages.success(request,'GST Type changed, add gst number.')

            
            
            return redirect('Fin_Edit_Company_profile')
        else:
            return redirect('Fin_Edit_Company_profile')
    else:
        return redirect('/')
        
#End

# < ------------- Shemeem -------- > Manual Journals < ------------------------------- >
        
def Fin_manualJournals(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            cmp = com
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            cmp = com.company_id
        
        allmodules = Fin_Modules_List.objects.get(company_id = cmp,status = 'New')
        jrn = Fin_Manual_Journal.objects.filter(Company = cmp)
        return render(request,'company/Fin_Manual_Journal.html',{'allmodules':allmodules,'com':com, 'cmp':cmp,'data':data,'journals':jrn})
    else:
       return redirect('/')

def Fin_addJournal(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            cmp = com
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            cmp = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = cmp,status = 'New')
        acc = Fin_Chart_Of_Account.objects.filter(Company=cmp).order_by('account_name')
        vnd = Fin_Vendors.objects.filter(Company = cmp, status = 'Active')
        cust = Fin_Customers.objects.filter(Company = cmp, status = 'Active')
        emp = Employee.objects.filter(company = cmp, employee_status = 'Active')


        # Fetching last Journal and assigning upcoming ref no as current + 1
        # Also check for if any bill is deleted and ref no is continuos w r t the deleted Journal
        latest_jrn = Fin_Manual_Journal.objects.filter(Company = cmp).order_by('-id').first()

        new_number = int(latest_jrn.reference_no) + 1 if latest_jrn else 1

        if Fin_Manual_Journal_Reference.objects.filter(Company = cmp).exists():
            deleted = Fin_Manual_Journal_Reference.objects.get(Company = cmp)
            
            if deleted:
                while int(deleted.reference_no) >= new_number:
                    new_number+=1

        # Finding next Jrn number w r t last Jrn number if exists.
        nxtJRN = ""
        if latest_jrn:
            jrn_no = str(latest_jrn.journal_no)
            numbers = []
            stri = []
            for word in jrn_no:
                if word.isdigit():
                    numbers.append(word)
                else:
                    stri.append(word)
            
            num=''
            for i in numbers:
                num +=i
            
            st = ''
            for j in stri:
                st = st+j

            journal_num = int(num)+1

            if num[0] == '0':
                if journal_num <10:
                    nxtJRN = st+'0'+ str(journal_num)
                else:
                    nxtJRN = st+ str(journal_num)
            else:
                nxtJRN = st+ str(journal_num)

        context = {
            'allmodules':allmodules, 'com':com, 'cmp':cmp, 'data':data, 'customers':cust, 'vendors':vnd, 'employees':emp,
            'ref_no':new_number,'JRNNo':nxtJRN, 'accounts':acc
        }
        return render(request,'company/Fin_Add_Journal.html',context)
    else:
       return redirect('/')

def Fin_checkJournalNumber(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        JrnNo = request.GET['JrnNum']

        nxtJrnNo = ""
        lastJournal = Fin_Manual_Journal.objects.filter(Company = com).last()
        if lastJournal:
            Jrn_no = str(lastJournal.journal_no)
            numbers = []
            stri = []
            for word in Jrn_no:
                if word.isdigit():
                    numbers.append(word)
                else:
                    stri.append(word)
            
            num=''
            for i in numbers:
                num +=i
            
            st = ''
            for j in stri:
                st = st+j

            journal_num = int(num)+1

            if num[0] == '0':
                if journal_num <10:
                    nxtJrnNo = st+'0'+ str(journal_num)
                else:
                    nxtJrnNo = st+ str(journal_num)
            else:
                nxtJrnNo = st+ str(journal_num)

        PatternStr = []
        for word in JrnNo:
            if word.isdigit():
                pass
            else:
                PatternStr.append(word)
        
        pattern = ''
        for j in PatternStr:
            pattern += j

        pattern_exists = checkJournalNumberPattern(pattern)

        if pattern !="" and pattern_exists:
            return JsonResponse({'status':False, 'message':'Journal No. Pattern already Exists.!'})
        elif Fin_Manual_Journal.objects.filter(Company = com, journal_no__iexact = JrnNo).exists():
            return JsonResponse({'status':False, 'message':'Journal No. already Exists.!'})
        elif nxtJrnNo != "" and JrnNo != nxtJrnNo:
            return JsonResponse({'status':False, 'message':'Journal No. is not continuous.!'})
        else:
            return JsonResponse({'status':True, 'message':'Number is okay.!'})
    else:
       return redirect('/')

def checkJournalNumberPattern(pattern):
    models = [Fin_Invoice, Fin_Sales_Order, Fin_Recurring_Invoice, Fin_Purchase_Bill, Fin_Estimate]

    for model in models:
        field_name = model.getNumFieldName(model)
        if model.objects.filter(**{f"{field_name}__icontains": pattern}).exists():
            return True
    return False

def Fin_createJournal(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        if request.method == 'POST':
            JRNNo = request.POST['journal_no']

            PatternStr = []
            for word in JRNNo:
                if word.isdigit():
                    pass
                else:
                    PatternStr.append(word)
            
            pattern = ''
            for j in PatternStr:
                pattern += j

            pattern_exists = checkJournalNumberPattern(pattern)

            if pattern !="" and pattern_exists:
                res = f'<script>alert("Journal No. Pattern already Exists.! Try another!");window.history.back();</script>'
                return HttpResponse(res)

            if Fin_Manual_Journal.objects.filter(Company = com, journal_no__iexact = JRNNo).exists():
                res = f'<script>alert("Journal Number `{JRNNo}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)
            
            debSubTot = request.POST['subtotal_debit']
            credSubTot = request.POST['subtotal_credit']

            debTot = request.POST['total_debit']
            credTot = request.POST['total_credit']

            Journal = Fin_Manual_Journal(
                Company = com,
                LoginDetails = com.Login_Id,
                reference_no = request.POST['reference_number'],
                journal_no = JRNNo,
                journal_date = request.POST['journal_date'],
                notes = request.POST['notes'],
                currency = request.POST['currency'],
                subtotal_debit = 0.0 if debSubTot == "" else float(debSubTot),
                subtotal_credit = 0.0 if credSubTot == "" else float(credSubTot),
                total_debit = 0.0 if debTot == "" else float(debTot),
                total_credit = 0.0 if credTot == "" else float(credTot),
                balance_debit = 0.0 if request.POST['balance_debit'] == "" else float(request.POST['balance_debit']),
                balance_credit = 0.0 if request.POST['balance_credit'] == "" else float(request.POST['balance_credit'])
            )

            if len(request.FILES) != 0:
                Journal.file=request.FILES.get('file')

            if 'Draft' in request.POST:
                Journal.status = "Draft"
            elif "Save" in request.POST:
                Journal.status = "Saved"

            if Journal.total_debit == Journal.total_credit:
                Journal.save()

                # Save Journal Accounts.

                accId = request.POST.getlist("acc_id[]")
                accName = request.POST.getlist("account_name[]")
                desc  = request.POST.getlist("desc[]")
                contact = request.POST.getlist("contact[]")
                deb = request.POST.getlist("debits[]")
                cred = request.POST.getlist("credits[]")

                debit = [0.0 if x == '' else float(x) for x in deb]
                credit = [0.0 if x == '' else float(x) for x in cred]

                if len(accId)==len(accName)==len(desc)==len(contact)==len(debit)==len(credit) and accId and accName and desc and contact and debit and credit:
                    mapped = zip(accId,accName,desc,contact,debit,credit)
                    mapped = list(mapped)
                    for ele in mapped:
                        acc = None if not ele[0].isdigit() else Fin_Chart_Of_Account.objects.get(id = int(ele[0]))
                        Fin_Manual_Journal_Accounts.objects.create(Journal = Journal, Account = acc, description = ele[2], contact = ele[3], debit = float(ele[4]), credit = float(ele[5]), Company = com, LoginDetails = com.Login_Id)
                
                # Save transaction
                        
                Fin_Manual_Journal_History.objects.create(
                    Company = com,
                    LoginDetails = data,
                    Journal = Journal,
                    action = 'Created'
                )

                return redirect(Fin_manualJournals)
            
            else:
                res = f'<script>alert("Please ensure that the debit and credit are equal.!");window.history.back();</script>'
                return HttpResponse(res)
        else:
            return redirect(Fin_addJournal)
    else:
       return redirect('/')

def Fin_createNewAccountAjax(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        if request.method == 'POST':
            name = request.POST['account_name']
            type = request.POST['account_type']
            subAcc = True if request.POST['subAccountCheckBox'] == 'true' else False
            parentAcc = request.POST['parent_account'] if subAcc == True else None
            accCode = request.POST['account_code']
            bankAccNum = None
            desc = request.POST['description']
            
            createdDate = date.today()
            
            #save account and transaction if account doesn't exists already
            if Fin_Chart_Of_Account.objects.filter(Company=com, account_name__iexact=name).exists():
                return JsonResponse({'status':False, 'message':'Account Name already exists..!'})
            else:
                account = Fin_Chart_Of_Account(
                    Company = com,
                    LoginDetails = data,
                    account_type = type,
                    account_name = name,
                    account_code = accCode,
                    description = desc,
                    balance = 0.0,
                    balance_type = None,
                    credit_card_no = None,
                    sub_account = subAcc,
                    parent_account = parentAcc,
                    bank_account_no = bankAccNum,
                    date = createdDate,
                    create_status = 'added',
                    status = 'active'
                )
                account.save()

                #save transaction

                Fin_ChartOfAccount_History.objects.create(
                    Company = com,
                    LoginDetails = data,
                    account = account,
                    action = 'Created'
                )
                
                list= []
                account_objects = Fin_Chart_Of_Account.objects.filter(Company=com).order_by('account_name')

                for account in account_objects:
                    accounts = {
                        'id':account.id,
                        'name': account.account_name,
                    }
                    list.append(accounts)

                return JsonResponse({'status':True,'accounts':list},safe=False)

        return JsonResponse({'status':False, 'message':'Something went wrong.!'})
    else:
       return redirect('/')

def Fin_viewJournal(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)

        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            cmp = com
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            cmp = com.company_id
        
        allmodules = Fin_Modules_List.objects.get(company_id = cmp,status = 'New')
        Jrn = Fin_Manual_Journal.objects.get(id = id)
        cmt = Fin_Manual_Journal_Comments.objects.filter(Journal = Jrn)
        hist = Fin_Manual_Journal_History.objects.filter(Journal = Jrn).last()
        JrnAcc = Fin_Manual_Journal_Accounts.objects.filter(Journal = Jrn)
        try:
            created = Fin_Manual_Journal_History.objects.get(Journal = Jrn, action = 'Created')
        except:
            created = None

        return render(request,'company/Fin_View_Journal.html',{'allmodules':allmodules,'com':com,'cmp':cmp, 'data':data, 'journal':Jrn,'jrnAccounts':JrnAcc, 'history':hist, 'comments':cmt, 'created':created})
    else:
       return redirect('/')

def Fin_editJournal(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            cmp = com
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            cmp = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = cmp,status = 'New')
        jrn = Fin_Manual_Journal.objects.get(id = id)
        jrnAcc = Fin_Manual_Journal_Accounts.objects.filter(Journal = jrn)
        acc = Fin_Chart_Of_Account.objects.filter(Company=cmp).order_by('account_name')
        vnd = Fin_Vendors.objects.filter(Company = cmp, status = 'Active')
        cust = Fin_Customers.objects.filter(Company = cmp, status = 'Active')
        emp = Employee.objects.filter(company = cmp, employee_status = 'Active')

        context = {
            'allmodules':allmodules, 'com':com, 'cmp':cmp, 'data':data,'journal':jrn, 'jrnAccounts':jrnAcc, 'customers':cust, 'vendors':vnd, 'employees':emp, 'accounts':acc
        }
        return render(request,'company/Fin_Edit_Journal.html',context)
    else:
       return redirect('/')

def Fin_updateJournal(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        jrn = Fin_Manual_Journal.objects.get(id = id)
        if request.method == 'POST':
            JRNNo = request.POST['journal_no']

            PatternStr = []
            for word in JRNNo:
                if word.isdigit():
                    pass
                else:
                    PatternStr.append(word)
            
            pattern = ''
            for j in PatternStr:
                pattern += j

            pattern_exists = checkJournalNumberPattern(pattern)

            if pattern !="" and pattern_exists:
                res = f'<script>alert("Journal No. Pattern already Exists.! Try another!");window.history.back();</script>'
                return HttpResponse(res)

            if jrn.journal_no != JRNNo and Fin_Manual_Journal.objects.filter(Company = com, journal_no__iexact = JRNNo).exists():
                res = f'<script>alert("Journal Number `{JRNNo}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)

            debSubTot = request.POST['subtotal_debit']
            credSubTot = request.POST['subtotal_credit']

            debTot = request.POST['total_debit']
            credTot = request.POST['total_credit']

            jrn.journal_no = JRNNo
            jrn.journal_date = request.POST['journal_date']
            jrn.notes = request.POST['notes']
            jrn.currency = request.POST['currency']
            jrn.subtotal_debit = 0.0 if debSubTot == "" else float(debSubTot)
            jrn.subtotal_credit = 0.0 if credSubTot == "" else float(credSubTot)
            jrn.total_debit = 0.0 if debTot == "" else float(debTot)
            jrn.total_credit = 0.0 if credTot == "" else float(credTot)
            jrn.balance_debit = 0.0 if request.POST['balance_debit'] == "" else float(request.POST['balance_debit'])
            jrn.balance_credit = 0.0 if request.POST['balance_credit'] == "" else float(request.POST['balance_credit'])

            if len(request.FILES) != 0:
                jrn.file=request.FILES.get('file')

            if debTot == credTot:
                jrn.save()

                # Save journal accounts.

                accId = request.POST.getlist("acc_id[]")
                accName = request.POST.getlist("account_name[]")
                desc  = request.POST.getlist("desc[]")
                contact = request.POST.getlist("contact[]")
                deb = request.POST.getlist("debits[]")
                cred = request.POST.getlist("credits[]")

                debit = [0.0 if x == '' else float(x) for x in deb]
                credit = [0.0 if x == '' else float(x) for x in cred]

                jrn_acc_ids = request.POST.getlist("id[]")
                JrnAcc_ids = [int(id) for id in jrn_acc_ids]

                journal_accs = Fin_Manual_Journal_Accounts.objects.filter(Journal = jrn)
                object_ids = [obj.id for obj in journal_accs]

                ids_to_delete = [obj_id for obj_id in object_ids if obj_id not in JrnAcc_ids]

                Fin_Manual_Journal_Accounts.objects.filter(id__in=ids_to_delete).delete()
                
                count = Fin_Manual_Journal_Accounts.objects.filter(Journal = jrn).count()

                if len(accId)==len(accName)==len(desc)==len(contact)==len(debit)==len(credit)==len(JrnAcc_ids) and JrnAcc_ids and accId and accName and desc and contact and debit and credit:
                    mapped = zip(accId,accName,desc,contact,debit,credit,JrnAcc_ids)
                    mapped = list(mapped)
                    for ele in mapped:
                        if int(len(accId))>int(count):
                            if ele[6] == 0:
                                acc = None if not ele[0].isdigit() else Fin_Chart_Of_Account.objects.get(id = int(ele[0]))
                                Fin_Manual_Journal_Accounts.objects.create(Journal = jrn, Account = acc, description = ele[2], contact = ele[3], debit = float(ele[4]), credit = float(ele[5]), Company = com, LoginDetails = com.Login_Id)
                            else:
                                acc = None if not ele[0].isdigit() else Fin_Chart_Of_Account.objects.get(id = int(ele[0]))
                                Fin_Manual_Journal_Accounts.objects.filter( id = int(ele[6])).update(Journal = jrn, Account = acc, description = ele[2], contact = ele[3], debit = float(ele[4]), credit = float(ele[5]))
                        else:
                            acc = None if not ele[0].isdigit() else Fin_Chart_Of_Account.objects.get(id = int(ele[0]))
                            Fin_Manual_Journal_Accounts.objects.filter( id = int(ele[6])).update(Journal = jrn, Account = acc, description = ele[2], contact = ele[3], debit = float(ele[4]), credit = float(ele[5]))
                
                # Save transaction
                        
                Fin_Manual_Journal_History.objects.create(
                    Company = com,
                    LoginDetails = data,
                    Journal = jrn,
                    action = 'Edited'
                )

                return redirect(Fin_viewJournal, id)
            else:
                res = f'<script>alert("Please ensure that the debit and credit are equal.!");window.history.back();</script>'
                return HttpResponse(res)
        else:
            return redirect(Fin_editJournal, id)
    else:
       return redirect('/')

def Fin_convertJournal(request,id):
    if 's_id' in request.session:

        jrn = Fin_Manual_Journal.objects.get(id = id)
        jrn.status = 'Saved'
        jrn.save()
        return redirect(Fin_viewJournal, id)

def Fin_journalHistory(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)

        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            cmp = com
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            cmp = com.company_id
        
        allmodules = Fin_Modules_List.objects.get(company_id = cmp,status = 'New')
        jrn = Fin_Manual_Journal.objects.get(id = id)
        his = Fin_Manual_Journal_History.objects.filter(Journal = jrn)

        return render(request,'company/Fin_Journal_History.html',{'allmodules':allmodules,'com':com,'data':data,'history':his, 'journal':jrn})
    else:
       return redirect('/')

def Fin_deleteJournal(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        jrn = Fin_Manual_Journal.objects.get( id = id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        Fin_Manual_Journal_Accounts.objects.filter(Journal = jrn).delete()

        # Storing ref number to deleted table
        # if entry exists and lesser than the current, update and save => Only one entry per company
        if Fin_Manual_Journal_Reference.objects.filter(Company = com).exists():
            deleted = Fin_Manual_Journal_Reference.objects.get(Company = com)
            if int(jrn.reference_no) > int(deleted.reference_no):
                deleted.reference_no = jrn.reference_no
                deleted.save()
        else:
            Fin_Manual_Journal_Reference.objects.create(Company = com, reference_no = jrn.reference_no)
        
        jrn.delete()
        return redirect(Fin_manualJournals)

def Fin_addJournalComment(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        jrn = Fin_Manual_Journal.objects.get(id = id)
        if request.method == "POST":
            cmt = request.POST['comment'].strip()

            Fin_Manual_Journal_Comments.objects.create(Company = com, Journal = jrn, comments = cmt)
            return redirect(Fin_viewJournal, id)
        return redirect(Fin_viewJournal, id)
    return redirect('/')

def Fin_deleteJournalComment(request,id):
    if 's_id' in request.session:
        cmt = Fin_Manual_Journal_Comments.objects.get(id = id)
        jrnId = cmt.Journal.id
        cmt.delete()
        return redirect(Fin_viewJournal, jrnId)

def Fin_attachJournalFile(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        jrn = Fin_Manual_Journal.objects.get(id = id)

        if request.method == 'POST' and len(request.FILES) != 0:
            jrn.file = request.FILES.get('file')
            jrn.save()

        return redirect(Fin_viewJournal, id)
    else:
        return redirect('/')

def Fin_journalPdf(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        jrn = Fin_Manual_Journal.objects.get(id = id)
        accs = Fin_Manual_Journal_Accounts.objects.filter(Journal = jrn)
    
        context = {'journal':jrn, 'jrnAccounts':accs,'cmp':com}
        
        template_path = 'company/Fin_Journal_Pdf.html'
        fname = 'Manual_Journal_' + jrn.journal_no

        # Create a Django response object, and specify content_type as pdftemp_
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] =f'attachment; filename = {fname}.pdf'
        # find the template and render it.
        template = get_template(template_path)
        html = template.render(context)

        # create a pdf
        pisa_status = pisa.CreatePDF(
        html, dest=response)
        # if error then show some funny view
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
    else:
        return redirect('/')

def Fin_shareJournalToEmail(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        jrn = Fin_Manual_Journal.objects.get(id = id)
        accs = Fin_Manual_Journal_Accounts.objects.filter(Journal = jrn)
        try:
            if request.method == 'POST':
                emails_string = request.POST['email_ids']

                # Split the string by commas and remove any leading or trailing whitespace
                emails_list = [email.strip() for email in emails_string.split(',')]
                email_message = request.POST['email_message']
                # print(emails_list)
            
                context = {'journal':jrn, 'jrnAccounts':accs,'cmp':com}
                template_path = 'company/Fin_Journal_Pdf.html'
                template = get_template(template_path)

                html  = template.render(context)
                result = BytesIO()
                pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
                pdf = result.getvalue()
                filename = f'Manual_Journal_{jrn.journal_no}'
                subject = f"Manual_Journal_{jrn.journal_no}"
                email = EmailMessage(subject, f"Hi,\nPlease find the attached Manual Journal for - #-{jrn.journal_no}. \n{email_message}\n\n--\nRegards,\n{com.Company_name}\n{com.Address}\n{com.State} - {com.Country}\n{com.Contact}", from_email=settings.EMAIL_HOST_USER, to=emails_list)
                email.attach(filename, pdf, "application/pdf")
                email.send(fail_silently=False)

                messages.success(request, 'Journal details has been shared via email successfully..!')
                return redirect(Fin_viewJournal,id)
        except Exception as e:
            print(e)
            messages.error(request, f'{e}')
            return redirect(Fin_viewJournal, id)
            
#End

# < ------------- Shemeem -------- > Recurring Invoice < ------------------------------- >

def Fin_recurringInvoice(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            cmp = com
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            cmp = com.company_id
        
        allmodules = Fin_Modules_List.objects.get(company_id = cmp,status = 'New')
        rec_inv = Fin_Recurring_Invoice.objects.filter(Company = cmp)
        return render(request,'company/Fin_Recurring_Invoice.html',{'allmodules':allmodules,'com':com,'data':data,'rec_invoices':rec_inv})
    else:
       return redirect('/')
    
def Fin_addRecurringInvoice(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            cmp = com
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            cmp = com.company_id

        cust = Fin_Customers.objects.filter(Company = cmp, status = 'Active')
        itms = Fin_Items.objects.filter(Company = cmp, status = 'Active')
        trms = Fin_Company_Payment_Terms.objects.filter(Company = cmp)
        bnk = Fin_Banking.objects.filter(company = cmp)
        lst = Fin_Price_List.objects.filter(Company = cmp, status = 'Active')
        units = Fin_Units.objects.filter(Company = cmp)
        priceList = Fin_Price_List.objects.filter(Company = cmp, type = 'Sales', status = 'Active')
        acc = Fin_Chart_Of_Account.objects.filter(Q(account_type='Expense') | Q(account_type='Other Expense') | Q(account_type='Cost Of Goods Sold'), Company=cmp).order_by('account_name')
        repeat = Fin_CompanyRepeatEvery.objects.filter(company = cmp)

        # Fetching last rec_invoice and assigning upcoming ref no as current + 1
        # Also check for if any bill is deleted and ref no is continuos w r t the deleted rec_invoice
        latest_inv = Fin_Recurring_Invoice.objects.filter(Company = cmp).order_by('-id').first()

        new_number = int(latest_inv.reference_no) + 1 if latest_inv else 1

        if Fin_Recurring_Invoice_Reference.objects.filter(Company = cmp).exists():
            deleted = Fin_Recurring_Invoice_Reference.objects.get(Company = cmp)
            
            if deleted:
                while int(deleted.reference_no) >= new_number:
                    new_number+=1

        # Finding next rec_invoice number w r t last rec_invoice number if exists.
        nxtInv = ""
        lastInv = Fin_Recurring_Invoice.objects.filter(Company = cmp).last()
        if lastInv:
            inv_no = str(lastInv.rec_invoice_no)
            numbers = []
            stri = []
            for word in inv_no:
                if word.isdigit():
                    numbers.append(word)
                else:
                    stri.append(word)
            
            num=''
            for i in numbers:
                num +=i
            
            st = ''
            for j in stri:
                st = st+j

            inv_num = int(num)+1

            if num[0] == '0':
                if inv_num <10:
                    nxtInv = st+'0'+ str(inv_num)
                else:
                    nxtInv = st+ str(inv_num)
            else:
                nxtInv = st+ str(inv_num)
        else:
            nxtInv = 'RI01'

        context = {
            'allmodules':allmodules, 'com':com, 'cmp':cmp, 'data':data, 'customers':cust, 'items':itms, 'pTerms':trms,'list':lst,
            'ref_no':new_number,'banks':bnk,'invNo':nxtInv,'units':units, 'accounts':acc, 'priceListItems':priceList, 'repeat':repeat,
        }
        return render(request,'company/Fin_Add_Recurring_Invoice.html',context)
    else:
       return redirect('/')

def Fin_checkRecurringInvoiceNumber(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        RecInvNo = request.GET['RecInvNum']

        # Finding next rec_invoice number w r t last rec_invoice number if exists.
        nxtInv = ""
        lastInv = Fin_Recurring_Invoice.objects.filter(Company = com).last()
        if lastInv:
            inv_no = str(lastInv.rec_invoice_no)
            numbers = []
            stri = []
            for word in inv_no:
                if word.isdigit():
                    numbers.append(word)
                else:
                    stri.append(word)
            
            num=''
            for i in numbers:
                num +=i
            
            st = ''
            for j in stri:
                st = st+j

            inv_num = int(num)+1

            if num[0] == '0':
                if inv_num <10:
                    nxtInv = st+'0'+ str(inv_num)
                else:
                    nxtInv = st+ str(inv_num)
            else:
                nxtInv = st+ str(inv_num)
        # else:
        #     nxtInv = 'RI01'

        PatternStr = []
        for word in RecInvNo:
            if word.isdigit():
                pass
            else:
                PatternStr.append(word)
        
        pattern = ''
        for j in PatternStr:
            pattern += j

        pattern_exists = checkRecInvNumberPattern(pattern)

        if pattern !="" and pattern_exists:
            return JsonResponse({'status':False, 'message':'Rec. Invoice No. Pattern already Exists.!'})
        elif Fin_Recurring_Invoice.objects.filter(Company = com, rec_invoice_no__iexact = RecInvNo).exists():
            return JsonResponse({'status':False, 'message':'Rec. Invoice No. already Exists.!'})
        elif nxtInv != "" and RecInvNo != nxtInv:
            return JsonResponse({'status':False, 'message':'Rec. Invoice No. is not continuous.!'})
        else:
            return JsonResponse({'status':True, 'message':'Number is okay.!'})
    else:
       return redirect('/')

def checkRecInvNumberPattern(pattern):
    models = [Fin_Invoice, Fin_Sales_Order, Fin_Estimate, Fin_Purchase_Bill, Fin_Manual_Journal]

    for model in models:
        field_name = model.getNumFieldName(model)
        if model.objects.filter(**{f"{field_name}__icontains": pattern}).exists():
            return True
    return False

def Fin_createRecurringInvoice(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        if request.method == 'POST':
            invNum = request.POST['rec_invoice_no']
            if Fin_Recurring_Invoice.objects.filter(Company = com, rec_invoice_no__iexact = invNum).exists():
                res = f'<script>alert("Rec. Invoice Number `{invNum}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)

            inv = Fin_Recurring_Invoice(
                Company = com,
                LoginDetails = com.Login_Id,
                Customer = Fin_Customers.objects.get(id = request.POST['customerId']),
                customer_email = request.POST['customerEmail'],
                billing_address = request.POST['bill_address'],
                gst_type = request.POST['gst_type'],
                gstin = request.POST['gstin'],
                place_of_supply = request.POST['place_of_supply'],
                profile_name = request.POST['profile_name'],
                entry_type = None if request.POST['entry_type'] == "" else request.POST['entry_type'],
                reference_no = request.POST['reference_number'],
                rec_invoice_no = invNum,
                payment_terms = Fin_Company_Payment_Terms.objects.get(id = request.POST['payment_term']),
                start_date = request.POST['start_date'],
                end_date = datetime.strptime(request.POST['end_date'], '%d-%m-%Y').date(),
                salesOrder_no = request.POST['order_number'],
                price_list_applied = True if 'priceList' in request.POST else False,
                price_list = None if request.POST['price_list_id'] == "" else Fin_Price_List.objects.get(id = request.POST['price_list_id']),
                repeat_every = Fin_CompanyRepeatEvery.objects.get(id = request.POST['repeat_every']),
                payment_method = None if request.POST['payment_method'] == "" else request.POST['payment_method'],
                cheque_no = None if request.POST['cheque_id'] == "" else request.POST['cheque_id'],
                upi_no = None if request.POST['upi_id'] == "" else request.POST['upi_id'],
                bank_acc_no = None if request.POST['bnk_id'] == "" else request.POST['bnk_id'],
                subtotal = 0.0 if request.POST['subtotal'] == "" else float(request.POST['subtotal']),
                igst = 0.0 if request.POST['igst'] == "" else float(request.POST['igst']),
                cgst = 0.0 if request.POST['cgst'] == "" else float(request.POST['cgst']),
                sgst = 0.0 if request.POST['sgst'] == "" else float(request.POST['sgst']),
                tax_amount = 0.0 if request.POST['taxamount'] == "" else float(request.POST['taxamount']),
                adjustment = 0.0 if request.POST['adj'] == "" else float(request.POST['adj']),
                shipping_charge = 0.0 if request.POST['ship'] == "" else float(request.POST['ship']),
                grandtotal = 0.0 if request.POST['grandtotal'] == "" else float(request.POST['grandtotal']),
                paid_off = 0.0 if request.POST['advance'] == "" else float(request.POST['advance']),
                balance = request.POST['grandtotal'] if request.POST['balance'] == "" else float(request.POST['balance']),
                note = request.POST['note']
            )

            inv.save()

            if len(request.FILES) != 0:
                inv.file=request.FILES.get('file')
            inv.save()

            if 'Draft' in request.POST:
                inv.status = "Draft"
            elif "Save" in request.POST:
                inv.status = "Saved" 
            inv.save()

            # Save rec_invoice items.

            itemId = request.POST.getlist("item_id[]")
            itemName = request.POST.getlist("item_name[]")
            hsn  = request.POST.getlist("hsn[]")
            qty = request.POST.getlist("qty[]")
            price = request.POST.getlist("priceListPrice[]") if 'priceList' in request.POST else request.POST.getlist("price[]")
            tax = request.POST.getlist("taxGST[]") if request.POST['place_of_supply'] == com.State else request.POST.getlist("taxIGST[]")
            discount = request.POST.getlist("discount[]")
            total = request.POST.getlist("total[]")

            if len(itemId)==len(itemName)==len(hsn)==len(qty)==len(price)==len(tax)==len(discount)==len(total) and itemId and itemName and hsn and qty and price and tax and discount and total:
                mapped = zip(itemId,itemName,hsn,qty,price,tax,discount,total)
                mapped = list(mapped)
                for ele in mapped:
                    itm = Fin_Items.objects.get(id = int(ele[0]))
                    Fin_Recurring_Invoice_Items.objects.create(RecInvoice = inv, Item = itm, hsn = ele[2], quantity = int(ele[3]), price = float(ele[4]), tax = ele[5], discount = float(ele[6]), total = float(ele[7]))
                    itm.current_stock -= int(ele[3])
                    itm.save()
            
            # Save transaction
                    
            Fin_Recurring_Invoice_History.objects.create(
                Company = com,
                LoginDetails = data,
                RecInvoice = inv,
                action = 'Created'
            )

            return redirect(Fin_recurringInvoice)
        else:
            return redirect(Fin_addRecurringInvoice)
    else:
       return redirect('/')

def Fin_viewRecurringInvoice(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)

        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            cmp = com
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            cmp = com.company_id
        
        allmodules = Fin_Modules_List.objects.get(company_id = cmp,status = 'New')
        recInv = Fin_Recurring_Invoice.objects.get(id = id)
        cmt = Fin_Recurring_Invoice_Comments.objects.filter(RecInvoice = recInv)
        hist = Fin_Recurring_Invoice_History.objects.filter(RecInvoice = recInv).last()
        invItems = Fin_Recurring_Invoice_Items.objects.filter(RecInvoice = recInv)
        created = Fin_Recurring_Invoice_History.objects.get(RecInvoice = recInv, action = 'Created')

        context = {
            'allmodules':allmodules,'com':com,'cmp':cmp, 'data':data, 'recInvoice':recInv,'recInvItems':invItems, 'history':hist, 'comments':cmt, 'created':created
        }

        return render(request,'company/Fin_View_RecInvoice.html', context)
    else:
       return redirect('/')

def Fin_convertRecurringInvoice(request,id):
    if 's_id' in request.session:

        rec_inv = Fin_Recurring_Invoice.objects.get(id = id)
        rec_inv.status = 'Saved'
        rec_inv.save()
        return redirect(Fin_viewRecurringInvoice, id)

def Fin_addRecurringInvoiceComment(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        rec_inv = Fin_Recurring_Invoice.objects.get(id = id)
        if request.method == "POST":
            cmt = request.POST['comment'].strip()

            Fin_Recurring_Invoice_Comments.objects.create(Company = com, RecInvoice = rec_inv, comments = cmt)
            return redirect(Fin_viewRecurringInvoice, id)
        return redirect(Fin_viewRecurringInvoice, id)
    return redirect('/')

def Fin_deleteRecurringInvoiceComment(request,id):
    if 's_id' in request.session:
        cmt = Fin_Recurring_Invoice_Comments.objects.get(id = id)
        recInvId = cmt.RecInvoice.id
        cmt.delete()
        return redirect(Fin_viewRecurringInvoice, recInvId)
    
def Fin_recurringInvoiceHistory(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        rec_inv = Fin_Recurring_Invoice.objects.get(id = id)
        his = Fin_Recurring_Invoice_History.objects.filter(RecInvoice = rec_inv)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
        
        return render(request,'company/Fin_RecInvoice_History.html',{'allmodules':allmodules,'com':com,'data':data,'history':his, 'recInvoice':rec_inv})
    else:
       return redirect('/')
    
def Fin_deleteRecurringInvoice(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        recInv = Fin_Recurring_Invoice.objects.get( id = id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        for i in Fin_Recurring_Invoice_Items.objects.filter(RecInvoice = recInv):
            item = Fin_Items.objects.get(id = i.Item.id)
            item.current_stock += i.quantity
            item.save()
        
        Fin_Recurring_Invoice_Items.objects.filter(RecInvoice = recInv).delete()

        # Storing ref number to deleted table
        # if entry exists and lesser than the current, update and save => Only one entry per company
        if Fin_Recurring_Invoice_Reference.objects.filter(Company = com).exists():
            deleted = Fin_Recurring_Invoice_Reference.objects.get(Company = com)
            if int(recInv.reference_no) > int(deleted.reference_no):
                deleted.reference_no = recInv.reference_no
                deleted.save()
        else:
            Fin_Recurring_Invoice_Reference.objects.create(Company = com, LoginDetails = com.Login_Id, reference_no = recInv.reference_no)
        
        recInv.delete()
        return redirect(Fin_recurringInvoice)

def Fin_newRepeatEveryType(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        dur = int(request.POST['duration'])
        type = request.POST['type']

        d = 30 if type == 'Month' else 360
        dys = dur * d
        print(dur,d,dys)
        rep_every = str(dur)+" "+type

        if not Fin_CompanyRepeatEvery.objects.filter(company = com, repeat_every__iexact = rep_every).exists():
            Fin_CompanyRepeatEvery.objects.create(company = com, repeat_every = rep_every, repeat_type = type, duration = dur, days = dys)
            
            list= []
            rep = Fin_CompanyRepeatEvery.objects.filter(company = com)

            for r in rep:
                repDict = {
                    'repeat_every': r.repeat_every,
                    'id': r.id
                }
                list.append(repDict)

            return JsonResponse({'status':True,'terms':list},safe=False)
        else:
            return JsonResponse({'status':False, 'message':f'{rep_every} already exists, try another.!'})

    else:
        return redirect('/')

def Fin_recurringInvoicePdf(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        inv = Fin_Recurring_Invoice.objects.get(id = id)
        itms = Fin_Recurring_Invoice_Items.objects.filter(RecInvoice = inv)
    
        context = {'recInvoice':inv, 'recInvItems':itms,'cmp':com}
        
        template_path = 'company/Fin_RecInvoice_Pdf.html'
        fname = 'Recurring_Invoice_'+inv.rec_invoice_no
        # Create a Django response object, and specify content_type as pdftemp_
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] =f'attachment; filename = {fname}.pdf'
        # find the template and render it.
        template = get_template(template_path)
        html = template.render(context)

        # create a pdf
        pisa_status = pisa.CreatePDF(
        html, dest=response)
        # if error then show some funny view
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
    else:
        return redirect('/')

def Fin_shareRecurringInvoiceToEmail(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        inv = Fin_Recurring_Invoice.objects.get(id = id)
        itms = Fin_Recurring_Invoice_Items.objects.filter(RecInvoice = inv)
        try:
            if request.method == 'POST':
                emails_string = request.POST['email_ids']

                # Split the string by commas and remove any leading or trailing whitespace
                emails_list = [email.strip() for email in emails_string.split(',')]
                email_message = request.POST['email_message']
                # print(emails_list)
            
                context = {'recInvoice':inv, 'recInvItems':itms,'cmp':com}
                template_path = 'company/Fin_RecInvoice_Pdf.html'
                template = get_template(template_path)

                html  = template.render(context)
                result = BytesIO()
                pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
                pdf = result.getvalue()
                filename = f'Recurring Invoice_{inv.rec_invoice_no}'
                subject = f"Recurring_Invoice_{inv.rec_invoice_no}"
                email = EmailMessage(subject, f"Hi,\nPlease find the attached Recurring Invoice for - REC. INVOICE-{inv.rec_invoice_no}. \n{email_message}\n\n--\nRegards,\n{com.Company_name}\n{com.Address}\n{com.State} - {com.Country}\n{com.Contact}", from_email=settings.EMAIL_HOST_USER, to=emails_list)
                email.attach(filename, pdf, "application/pdf")
                email.send(fail_silently=False)

                messages.success(request, 'Rec. Invoice details has been shared via email successfully..!')
                return redirect(Fin_viewRecurringInvoice,id)
        except Exception as e:
            print(e)
            messages.error(request, f'{e}')
            return redirect(Fin_viewRecurringInvoice, id)

def Fin_editRecurringInvoice(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            cmp = com
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            cmp = com.company_id

        rec_inv = Fin_Recurring_Invoice.objects.get(id = id)
        recInvItms = Fin_Recurring_Invoice_Items.objects.filter(RecInvoice = rec_inv)

        cust = Fin_Customers.objects.filter(Company = cmp, status = 'Active')
        itms = Fin_Items.objects.filter(Company = cmp, status = 'Active')
        trms = Fin_Company_Payment_Terms.objects.filter(Company = cmp)
        bnk = Fin_Banking.objects.filter(company = cmp)
        lst = Fin_Price_List.objects.filter(Company = cmp, status = 'Active')
        units = Fin_Units.objects.filter(Company = cmp)
        priceList = Fin_Price_List.objects.filter(Company = cmp, type = 'Sales', status = 'Active')
        acc = Fin_Chart_Of_Account.objects.filter(Q(account_type='Expense') | Q(account_type='Other Expense') | Q(account_type='Cost Of Goods Sold'), Company=cmp).order_by('account_name')
        repeat = Fin_CompanyRepeatEvery.objects.filter(company = cmp)

        context = {
            'allmodules':allmodules, 'com':com, 'cmp':cmp, 'data':data,'recInvoice':rec_inv, 'recInvItems':recInvItms, 'customers':cust, 'items':itms, 'pTerms':trms,'list':lst,
            'banks':bnk,'units':units, 'accounts':acc, 'priceListItems':priceList, 'repeat':repeat,
        }
        return render(request,'company/Fin_Edit_RecInvoice.html',context)
    else:
       return redirect('/')

def Fin_updateRecurringInvoice(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        rec_inv = Fin_Recurring_Invoice.objects.get(id = id)
        if request.method == 'POST':
            invNum = request.POST['rec_invoice_no']
            if rec_inv.rec_invoice_no != invNum and Fin_Recurring_Invoice.objects.filter(Company = com, rec_invoice_no__iexact = invNum).exists():
                res = f'<script>alert("Recurring Invoice Number `{invNum}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)

            rec_inv.Customer = Fin_Customers.objects.get(id = request.POST['customerId'])
            rec_inv.customer_email = request.POST['customerEmail']
            rec_inv.billing_address = request.POST['bill_address']
            rec_inv.gst_type = request.POST['gst_type']
            rec_inv.gstin = request.POST['gstin']
            rec_inv.place_of_supply = request.POST['place_of_supply']
            rec_inv.profile_name = request.POST['profile_name']
            rec_inv.entry_type = None if request.POST['entry_type'] == "" else request.POST['entry_type']
            rec_inv.rec_invoice_no = invNum
            rec_inv.payment_terms = Fin_Company_Payment_Terms.objects.get(id = request.POST['payment_term'])
            rec_inv.start_date = request.POST['start_date']
            rec_inv.end_date = datetime.strptime(request.POST['end_date'], '%d-%m-%Y').date()
            rec_inv.salesOrder_no = request.POST['order_number']
            rec_inv.price_list_applied = True if 'priceList' in request.POST else False
            rec_inv.price_list = None if request.POST['price_list_id'] == "" else Fin_Price_List.objects.get(id = request.POST['price_list_id'])
            rec_inv.repeat_every = Fin_CompanyRepeatEvery.objects.get(id = request.POST['repeat_every'])
            rec_inv.payment_method = None if request.POST['payment_method'] == "" else request.POST['payment_method']
            rec_inv.cheque_no = None if request.POST['cheque_id'] == "" else request.POST['cheque_id']
            rec_inv.upi_no = None if request.POST['upi_id'] == "" else request.POST['upi_id']
            rec_inv.bank_acc_no = None if request.POST['bnk_id'] == "" else request.POST['bnk_id']
            rec_inv.subtotal = 0.0 if request.POST['subtotal'] == "" else float(request.POST['subtotal'])
            rec_inv.igst = 0.0 if request.POST['igst'] == "" else float(request.POST['igst'])
            rec_inv.cgst = 0.0 if request.POST['cgst'] == "" else float(request.POST['cgst'])
            rec_inv.sgst = 0.0 if request.POST['sgst'] == "" else float(request.POST['sgst'])
            rec_inv.tax_amount = 0.0 if request.POST['taxamount'] == "" else float(request.POST['taxamount'])
            rec_inv.adjustment = 0.0 if request.POST['adj'] == "" else float(request.POST['adj'])
            rec_inv.shipping_charge = 0.0 if request.POST['ship'] == "" else float(request.POST['ship'])
            rec_inv.grandtotal = 0.0 if request.POST['grandtotal'] == "" else float(request.POST['grandtotal'])
            rec_inv.paid_off = 0.0 if request.POST['advance'] == "" else float(request.POST['advance'])
            rec_inv.balance = request.POST['grandtotal'] if request.POST['balance'] == "" else float(request.POST['balance'])
            rec_inv.note = request.POST['note']

            if len(request.FILES) != 0:
                rec_inv.file=request.FILES.get('file')

            rec_inv.save()

            # Save invoice items.

            itemId = request.POST.getlist("item_id[]")
            itemName = request.POST.getlist("item_name[]")
            hsn  = request.POST.getlist("hsn[]")
            qty = request.POST.getlist("qty[]")
            price = request.POST.getlist("priceListPrice[]") if 'priceList' in request.POST else request.POST.getlist("price[]")
            tax = request.POST.getlist("taxGST[]") if request.POST['place_of_supply'] == com.State else request.POST.getlist("taxIGST[]")
            discount = request.POST.getlist("discount[]")
            total = request.POST.getlist("total[]")
            inv_item_ids = request.POST.getlist("id[]")
            invItem_ids = [int(id) for id in inv_item_ids]

            inv_items = Fin_Recurring_Invoice_Items.objects.filter(RecInvoice = rec_inv)
            object_ids = [obj.id for obj in inv_items]

            ids_to_delete = [obj_id for obj_id in object_ids if obj_id not in invItem_ids]
            for itmId in ids_to_delete:
                invItem = Fin_Recurring_Invoice_Items.objects.get(id = itmId)
                item = Fin_Items.objects.get(id = invItem.Item.id)
                item.current_stock += invItem.quantity
                item.save()

            Fin_Recurring_Invoice_Items.objects.filter(id__in=ids_to_delete).delete()
            
            count = Fin_Recurring_Invoice_Items.objects.filter(RecInvoice = rec_inv).count()

            if len(itemId)==len(itemName)==len(hsn)==len(qty)==len(price)==len(tax)==len(discount)==len(total)==len(invItem_ids) and invItem_ids and itemId and itemName and hsn and qty and price and tax and discount and total:
                mapped = zip(itemId,itemName,hsn,qty,price,tax,discount,total,invItem_ids)
                mapped = list(mapped)
                for ele in mapped:
                    if int(len(itemId))>int(count):
                        if ele[8] == 0:
                            itm = Fin_Items.objects.get(id = int(ele[0]))
                            Fin_Recurring_Invoice_Items.objects.create(RecInvoice = rec_inv, Item = itm, hsn = ele[2], quantity = int(ele[3]), price = float(ele[4]), tax = ele[5], discount = float(ele[6]), total = float(ele[7]))
                            itm.current_stock -= int(ele[3])
                            itm.save()
                        else:
                            itm = Fin_Items.objects.get(id = int(ele[0]))
                            inItm = Fin_Recurring_Invoice_Items.objects.get(id = int(ele[8]))
                            crQty = int(inItm.quantity)
                            
                            Fin_Recurring_Invoice_Items.objects.filter( id = int(ele[8])).update(RecInvoice = rec_inv, Item = itm, hsn = ele[2], quantity = int(ele[3]), price = float(ele[4]), tax = ele[5], discount = float(ele[6]), total = float(ele[7]))

                            if crQty < int(ele[3]):
                                itm.current_stock -=  abs(crQty - int(ele[3]))
                            elif crQty > int(ele[3]):
                                itm.current_stock += abs(crQty - int(ele[3]))
                            itm.save()
                    else:
                        itm = Fin_Items.objects.get(id = int(ele[0]))
                        inItm = Fin_Recurring_Invoice_Items.objects.get(id = int(ele[8]))
                        crQty = int(inItm.quantity)

                        Fin_Recurring_Invoice_Items.objects.filter( id = int(ele[8])).update(RecInvoice = rec_inv, Item = itm, hsn = ele[2], quantity = int(ele[3]), price = float(ele[4]), tax = ele[5], discount = float(ele[6]), total = float(ele[7]))

                        if crQty < int(ele[3]):
                            itm.current_stock -=  abs(crQty - int(ele[3]))
                        elif crQty > int(ele[3]):
                            itm.current_stock += abs(crQty - int(ele[3]))
                        itm.save()
            
            # Save transaction
                    
            Fin_Recurring_Invoice_History.objects.create(
                Company = com,
                LoginDetails = data,
                RecInvoice = rec_inv,
                action = 'Edited'
            )

            return redirect(Fin_viewRecurringInvoice, id)
        else:
            return redirect(Fin_editRecurringInvoice, id)
    else:
       return redirect('/')

# End

def Fin_Attendance(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        log = Fin_Login_Details.objects.get(id = s_id)
        
        if log.User_Type == 'Staff':
            event_counts = {}
            formatted_event_counts = {}
            staff =Fin_Staff_Details.objects.get(Login_Id =log)
            all_events = Fin_Attendances.objects.filter(company=staff.company_id)
            for event in all_events:
                month_year = event.start_date.strftime('%Y-%m')  # Format: 'YYYY-MM'
                year, month = map(int, month_year.split('-'))

                event_duration = (event.end_date - event.start_date).days + 1 if event.end_date else 1

                if month_year not in event_counts:
                    event_counts[month_year] = event_duration
                else:
                    event_counts[month_year] += event_duration
            for key, value in event_counts.items():
                year, month = map(int, key.split('-'))
                total_days = monthrange(year, month)[1]
                month_name = calendar.month_name[int(month)]
                formatted_month_year = f"{month_name}-{year}"
                formatted_event_counts[formatted_month_year] = {'count': value, 'total_days': total_days, 'month': month_name,
                                                         'year': year}
                
            attendance_data = Fin_Attendances.objects.filter(company=staff.company_id)
            employee_attendance = {}

            for entry in attendance_data:
                year = entry.start_date.year
                month = entry.start_date.month

                key = (entry.employee.id, year, month)
               
                if key not in employee_attendance:
                    formatted_month_year = f"{calendar.month_name[int(month)]}-{year}"
                    employee_attendance[key] = {
                    'formatted_month_year': formatted_month_year,
                    'e_id':entry.employee.id,
                    'employee': entry.employee.first_name + ' ' + entry.employee.last_name,
                    'year': year,
                    'month': calendar.month_name[int(month)],
                    'working_days': 0,
                    'holidays': 0,
                    'absent_days': 0,
                }

                if entry.status == 'Leave':
                    absent_days = (entry.end_date - entry.start_date).days + 1 if entry.end_date else 1
                    employee_attendance[key]['absent_days'] += absent_days

                    _, last_day = monthrange(year, month)

                holidays_data = Holiday.objects.filter(
                    company=staff.company_id,
                    start_date__year=year,
                    start_date__month=month
                )
                total_holidays = 0
                for holiday in holidays_data:
                    total_holidays += (holiday.end_date - holiday.start_date).days + 1

                employee_attendance[key]['holidays'] = total_holidays
                employee_attendance[key]['working_days'] = last_day - total_holidays - employee_attendance[key]['absent_days']
            

        if log.User_Type == 'Company':
            event_counts = {}
            formatted_event_counts = {}
            com = Fin_Company_Details.objects.get(Login_Id = log)
            all_events = Fin_Attendances.objects.filter(company=com.id)
            for event in all_events:
                month_year = event.start_date.strftime('%Y-%m')  # Format: 'YYYY-MM'
                year, month = map(int, month_year.split('-'))

                event_duration = (event.end_date - event.start_date).days + 1 if event.end_date else 1

                if month_year not in event_counts:
                    event_counts[month_year] = event_duration
                else:
                    event_counts[month_year] += event_duration
            for key, value in event_counts.items():
                year, month = map(int, key.split('-'))
                total_days = monthrange(year, month)[1]
                month_name = calendar.month_name[int(month)]
                formatted_month_year = f"{month_name}-{year}"
                formatted_event_counts[formatted_month_year] = {'count': value, 'total_days': total_days, 'month': month_name,
                                                         'year': year}
                
            attendance_data = Fin_Attendances.objects.filter(company=com.id)
            employee_attendance = {}

            for entry in attendance_data:
                year = entry.start_date.year
                month = entry.start_date.month

                key = (entry.employee.id, year, month)
               
                if key not in employee_attendance:
                    formatted_month_year = f"{calendar.month_name[int(month)]}-{year}"
                    employee_attendance[key] = {
                    'formatted_month_year': formatted_month_year,
                    'e_id':entry.employee.id,
                    'employee': entry.employee.first_name + ' ' + entry.employee.last_name,
                    'year': year,
                    'month': calendar.month_name[int(month)],
                    'working_days': 0,
                    'holidays': 0,
                    'absent_days': 0,
                }
            

                if entry.status == 'Leave':
                    absent_days = (entry.end_date - entry.start_date).days + 1 if entry.end_date else 1
                    employee_attendance[key]['absent_days'] += absent_days

                    _, last_day = monthrange(year, month)

                holidays_data = Holiday.objects.filter(
                    company=com.id,
                    start_date__year=year,
                    start_date__month=month
                )
                total_holidays = 0
                for holiday in holidays_data:
                    total_holidays += (holiday.end_date - holiday.start_date).days + 1

                employee_attendance[key]['holidays'] = total_holidays
                employee_attendance[key]['working_days'] = last_day - total_holidays - employee_attendance[key]['absent_days']
            

        context = {
            "events": all_events,
            "event_counts_json": formatted_event_counts,
            'employee_attendance': list(employee_attendance.values()),
        }   
        return render(request,'company/Fin_Attendance.html',context)





def Fin_Add_Attendance(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        log = Fin_Login_Details.objects.get(id = s_id)
        if log.User_Type == 'Staff':
            staff =Fin_Staff_Details.objects.get(Login_Id =log)
            emp = Employee.objects.filter(company = staff.company_id,employee_status = 'active')
            bgroup = Employee_Blood_Group.objects.filter(company = staff.company_id)
        if log.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = log)
            emp = Employee.objects.filter(company = com.id,employee_status = 'active')
            bgroup = Employee_Blood_Group.objects.filter(company = com.id)

        context ={
            'emp':emp,'bloodgroup':bgroup
        }
        return render(request,'company/Fin_add_attendance.html',context)
    return redirect('Fin_Attendance')




def Fin_Holiday_check_for_attendance(request):
    date = request.POST.get('sdate')
    empid = request.POST.get('empid')
    if 's_id' in request.session:
        s_id = request.session['s_id']
        log = Fin_Login_Details.objects.get(id = s_id)
        if log.User_Type == 'Staff':
            staff =Fin_Staff_Details.objects.get(Login_Id =log)
            exists = Holiday.objects.filter(company = staff.company_id,start_date__lte=date, end_date__gte=date).exists()
            atndance = Fin_Attendances.objects.filter(employee = empid, company = staff.company_id,start_date__lte=date,end_date__gte=date).exists()
        if log.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = log)
            exists = Holiday.objects.filter(company = com.id,start_date__lte=date, end_date__gte=date).exists()
            atndance = Fin_Attendances.objects.filter(employee = empid, company = com.id,start_date__lte=date,end_date__gte=date).exists()

        return JsonResponse({'exists': exists,'atndance':atndance})




def Fin_attendance_save(request):
    if 's_id' in request.session:
        if request.method == 'POST':
            s_id = request.session['s_id']
            emp = request.POST['emp']
            empid = Employee.objects.get(id = emp)
            log = Fin_Login_Details.objects.get(id = s_id)
            if log.User_Type == 'Staff':
                staff =Fin_Staff_Details.objects.get(Login_Id =log)
                attendance = Fin_Attendances(employee = empid,start_date= request.POST['sdate'],end_date = request.POST['edate'],status = request.POST['status'],reason = request.POST['reason'],company = staff.company_id,login_id = log)
                attendance.save()
                att_history = Fin_Attendance_history(company = staff.company_id,login_id = log,attendance = attendance,action = "Created")
                att_history.save()
                return redirect('Fin_Attendance')

            if log.User_Type == 'Company':
                com = Fin_Company_Details.objects.get(Login_Id = log)
                attendance = Fin_Attendances(start_date= request.POST['sdate'],end_date = request.POST['edate'],status = request.POST['status'],reason = request.POST['reason'],company = com,login_id = log,employee = empid)
                attendance.save()
                att_history = Fin_Attendance_history(company = com,login_id = log,attendance = attendance,action = "Created")
                att_history.save()
                return redirect('Fin_Attendance')
        return redirect('Fin_Add_Attendance')
    return redirect('Fin_Add_Attendance')




def fin_employee_save_atndnce(request):

    if request.method == 'POST':

        title = request.POST['Title']
        firstname = request.POST['First_Name'].capitalize()
        lastname = request.POST['Last_Name'].capitalize()
        image = request.FILES.get('Image', None)
        if image:
            image = request.FILES['Image']
        else:
            image = ''
        alias = request.POST['Alias']
        joiningdate = request.POST['Joining_Date']
        salarydate = request.POST['Salary_Date']
        salary_type = request.POST['Salary_Type']

        amountperhour = request.POST['perhour']
        if amountperhour == '' or amountperhour == '0':
            amountperhour = 0
        else:
            amountperhour = request.POST['perhour']

        workinghour = request.POST['workhour']
        if workinghour == '' or workinghour == '0':
            workinghour = 0
        else:
            workinghour = request.POST['workhour']

        salaryamount = request.POST['Salary_Amount']
        if request.POST['Salary_Amount'] == '':
            salaryamount = None
        else:
            salaryamount = request.POST['Salary_Amount']

        employeenumber = request.POST['Employee_Number']
        designation = request.POST['Designation']
        location = request.POST['Location']
        gender = request.POST['Gender']
        dob = request.POST['DOB']
        blood = request.POST['Blood']
        contact = request.POST['Contact_Number']
        emergencycontact = request.POST['Emergency_Contact']
        email = request.POST['Email']
        parent = request.POST['Parent'].capitalize()
        spouse = request.POST['Spouse'].capitalize()
        file = request.FILES.get('File', None)
        if file:
            file = request.FILES['File']
        else:
            file=''
        street = request.POST['street']
        city = request.POST['city']
        state = request.POST['state']
        pincode = request.POST['pincode']
        country = request.POST['country']
        tempStreet = request.POST['tempStreet']
        tempCity = request.POST['tempCity']
        tempState = request.POST['tempState']
        tempPincode = request.POST['tempPincode']
        tempCountry = request.POST['tempCountry']
        
        bankdetails = request.POST['Bank_Details']
        if bankdetails == "Yes":
            accoutnumber = request.POST['Account_Number']
            ifsc = request.POST['IFSC']
            bankname = request.POST['BankName']
            branchname = request.POST['BranchName']
            transactiontype = request.POST['Transaction_Type']
        else:
            accoutnumber = ''
            ifsc = ''
            bankname = ''
            branchname = ''
            transactiontype = ''

        if request.POST['tds_applicable'] == 'Yes':
            tdsapplicable = request.POST['tds_applicable']
            tdstype = request.POST['TDS_Type']
            
            if tdstype == 'Amount':
                tdsvalue = request.POST['TDS_Amount']
            elif tdstype == 'Percentage':
                tdsvalue = request.POST['TDS_Percentage']
            else:
                tdsvalue = 0
        elif request.POST['tds_applicable'] == 'No':
            tdsvalue = 0
            tdstype = ''
            tdsapplicable = request.POST['tds_applicable']
        else:
            tdsvalue = 0
            tdstype = ''
            tdsapplicable = ''

        incometax = request.POST['Income_Tax']
        aadhar = request.POST['Aadhar']
        uan = request.POST['UAN']
        pf = request.POST['PF']
        pan = request.POST['PAN']
        pr = request.POST['PR']

        if dob == '':
            age = 2
        else:
            dob2 = date.fromisoformat(dob)
            today = date.today()
            age = int(today.year - dob2.year - ((today.month, today.day) < (dob2.month, dob2.day)))
        
        sid = request.session['s_id']
        employee = Fin_Login_Details.objects.get(id=sid)
        
        if employee.User_Type == 'Company':
            companykey =  Fin_Company_Details.objects.get(Login_Id_id=sid)
        elif employee.User_Type == 'Staff':
            staffkey = Fin_Staff_Details.objects.get(Login_Id=sid)
            companykey = Fin_Company_Details.objects.get(id=staffkey.company_id_id)
        else:
            distributorkey = Fin_Distributors_Details.objects.get(login_Id=sid)
            companykey = Fin_Company_Details.objects.get(id=distributorkey.company_id_id)

        
        if Employee.objects.filter(employee_mail=email,mobile = contact,employee_number=employeenumber,company_id = companykey.id).exists():
            messages.error(request,'user exist')
            return redirect('Fin_Add_Attendance')
        
        elif Employee.objects.filter(mobile = contact,company_id = companykey.id).exists():
            messages.error(request,'phone number exist')
            return redirect('Fin_Add_Attendance')
        
        elif Employee.objects.filter(emergency_contact = emergencycontact,company_id = companykey.id).exists():
            messages.error(request,'emergency phone number exist')
            return redirect('Fin_Add_Attendance')
        
        elif Employee.objects.filter(employee_mail=email,company_id = companykey.id).exists():
            messages.error(request,'email exist')
            return redirect('Fin_Add_Attendance')
        
        elif Employee.objects.filter(employee_number=employeenumber,company_id = companykey.id).exists():
            messages.error(request,'employee id exist')
            return redirect('Fin_Add_Attendance')
        
        elif incometax != '' and Employee.objects.filter(income_tax_number = incometax,company_id = companykey.id).exists():
            messages.error(request,'Income Tax Number exist')
            return redirect('Fin_Add_Attendance')
        
        elif pf != '' and Employee.objects.filter(pf_account_number = pf,company_id = companykey.id).exists():
            messages.error(request,'PF account number exist')
            return redirect('Fin_Add_Attendance')
        
        elif aadhar != '' and Employee.objects.filter(aadhar_number = aadhar,company_id = companykey.id).exists():
            messages.error(request,'Aadhar number exist')
            return redirect('Fin_Add_Attendance')
        
        elif pan != '' and Employee.objects.filter(pan_number = pan,company_id = companykey.id).exists():
            messages.error(request,'PAN number exist')
            return redirect('Fin_Add_Attendance')
        
        elif uan != '' and Employee.objects.filter(universal_account_number = uan,company_id = companykey.id).exists():
            messages.error(request,'Universal account number exist')
            return redirect('Fin_Add_Attendance')
        
        elif pr != '' and Employee.objects.filter(pr_account_number = pr,company_id = companykey.id).exists():
            messages.error(request,'PR account number exist')
            return redirect('Fin_Add_Attendance')
        
        elif bankdetails.lower() == 'yes':
            if accoutnumber != '' and Employee.objects.filter(account_number=accoutnumber,company_id = companykey.id).exists():
                messages.error(request,'Bank account number already exist')
                return redirect('Fin_Add_Attendance')
            
            else:
                if employee.User_Type == 'Company':
                    

                    new = Employee(upload_image=image,title = title,first_name = firstname,last_name = lastname,alias = alias,
                            employee_mail = email,employee_number = employeenumber,employee_designation = designation,
                            employee_current_location = location,mobile = contact,date_of_joining = joiningdate,
                            employee_status = 'Active' ,company_id = companykey.id,login_id=sid,salary_amount = salaryamount ,
                            amount_per_hour = amountperhour ,total_working_hours = workinghour,gender = gender ,date_of_birth = dob ,
                            age = age,blood_group = blood,fathers_name_mothers_name = parent,spouse_name = spouse,
                            emergency_contact = emergencycontact,provide_bank_details = bankdetails,account_number = accoutnumber,
                            ifsc = ifsc,name_of_bank = bankname,branch_name = branchname,bank_transaction_type = transactiontype,
                            tds_applicable = tdsapplicable, tds_type = tdstype,percentage_amount = tdsvalue,pan_number = pan,
                            income_tax_number = incometax,aadhar_number = aadhar,universal_account_number = uan,pf_account_number = pf,
                            pr_account_number = pr,upload_file = file,employee_salary_type =salary_type,salary_effective_from=salarydate,
                            city=city,street=street,state=state,country=country,pincode=pincode,temporary_city=tempCity,
                            temporary_street=tempStreet,temporary_state=tempState,temporary_pincode=tempPincode,temporary_country=tempCountry)
                    new.save()

                    history = Employee_History(company_id = companykey.id,login_id=sid,employee_id = new.id,date = date.today(),action = 'Created')
                    history.save()
            
                elif employee.User_Type == 'Staff':
                    

                    new =  Employee(upload_image=image,title = title,first_name = firstname,last_name = lastname,alias = alias,
                                employee_mail = email,employee_number = employeenumber,employee_designation = designation,
                                employee_current_location = location,mobile = contact,date_of_joining = joiningdate,
                                employee_salary_type = salary_type,employee_status = 'Active' ,company_id = companykey.id,login_id=sid ,
                                amount_per_hour = amountperhour ,total_working_hours = workinghour,gender = gender ,date_of_birth = dob ,
                                age = age,blood_group = blood,fathers_name_mothers_name = parent,spouse_name = spouse,
                                emergency_contact = emergencycontact,provide_bank_details = bankdetails,account_number = accoutnumber,
                                ifsc = ifsc,name_of_bank = bankname,branch_name = branchname,bank_transaction_type = transactiontype,
                                tds_applicable = tdsapplicable, tds_type = tdstype,percentage_amount = tdsvalue,pan_number = pan,
                                income_tax_number = incometax,aadhar_number = aadhar,universal_account_number = uan,pf_account_number = pf,
                                pr_account_number = pr,upload_file = file,salary_amount = salaryamount,salary_effective_from=salarydate,
                                city=city,street=street,state=state,country=country,pincode=pincode,temporary_city=tempCity,
                                temporary_street=tempStreet,temporary_state=tempState,temporary_pincode=tempPincode,temporary_country=tempCountry)
                    
                    new.save()

                    history = Employee_History(company_id = companykey.id,login_id=sid,employee_id = new.id,date = date.today(),action = 'Created')
                    history.save()
        
        else:
            if employee.User_Type == 'Company':
                

                new = Employee(upload_image=image,title = title,first_name = firstname,last_name = lastname,alias = alias,
                        employee_mail = email,employee_number = employeenumber,employee_designation = designation,
                        employee_current_location = location,mobile = contact,date_of_joining = joiningdate,
                        employee_status = 'Active' ,company_id = companykey.id,login_id=sid,salary_amount = salaryamount ,
                        amount_per_hour = amountperhour ,total_working_hours = workinghour,gender = gender ,date_of_birth = dob ,
                        age = age,blood_group = blood,fathers_name_mothers_name = parent,spouse_name = spouse,
                        emergency_contact = emergencycontact,provide_bank_details = bankdetails,account_number = accoutnumber,
                        ifsc = ifsc,name_of_bank = bankname,branch_name = branchname,bank_transaction_type = transactiontype,
                        tds_applicable = tdsapplicable, tds_type = tdstype,percentage_amount = tdsvalue,pan_number = pan,
                        income_tax_number = incometax,aadhar_number = aadhar,universal_account_number = uan,pf_account_number = pf,
                        pr_account_number = pr,upload_file = file,employee_salary_type =salary_type,salary_effective_from=salarydate,
                        city=city,street=street,state=state,country=country,pincode=pincode,temporary_city=tempCity,
                        temporary_street=tempStreet,temporary_state=tempState,temporary_pincode=tempPincode,temporary_country=tempCountry)
                new.save()

                history = Employee_History(company_id = companykey.id,login_id=sid,employee_id = new.id,date = date.today(),action = 'Created')
                history.save()
        
            elif employee.User_Type == 'Staff':
                

                new =  Employee(upload_image=image,title = title,first_name = firstname,last_name = lastname,alias = alias,
                            employee_mail = email,employee_number = employeenumber,employee_designation = designation,
                            employee_current_location = location,mobile = contact,date_of_joining = joiningdate,
                            employee_salary_type = salary_type,employee_status = 'Active' ,company_id = companykey.id,login_id=sid ,
                            amount_per_hour = amountperhour ,total_working_hours = workinghour,gender = gender ,date_of_birth = dob ,
                            age = age,blood_group = blood,fathers_name_mothers_name = parent,spouse_name = spouse,
                            emergency_contact = emergencycontact,provide_bank_details = bankdetails,account_number = accoutnumber,
                            ifsc = ifsc,name_of_bank = bankname,branch_name = branchname,bank_transaction_type = transactiontype,
                            tds_applicable = tdsapplicable, tds_type = tdstype,percentage_amount = tdsvalue,pan_number = pan,
                            income_tax_number = incometax,aadhar_number = aadhar,universal_account_number = uan,pf_account_number = pf,
                            pr_account_number = pr,upload_file = file,salary_amount = salaryamount,salary_effective_from=salarydate,
                            city=city,street=street,state=state,country=country,pincode=pincode,temporary_city=tempCity,
                            temporary_street=tempStreet,temporary_state=tempState,temporary_pincode=tempPincode,temporary_country=tempCountry)
                
                new.save()

                history = Employee_History(company_id = companykey.id,login_id=sid,employee_id = new.id,date = date.today(),action = 'Created')
                history.save()

        sid = request.session['s_id']
        loginn = Fin_Login_Details.objects.get(id=sid)
        if loginn.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = sid)
            allmodules = Fin_Modules_List.objects.get(company_id = com.id)
            employee = Employee.objects.filter(company_id=com.id)
            
        elif loginn.User_Type == 'Staff' :
            com = Fin_Staff_Details.objects.get(Login_Id = sid)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
            employee = Employee.objects.filter(company_id=com.company_id_id)
        return redirect('Fin_Add_Attendance')




def Fin_Attendanceview(request,mn,yr,id):
    if 's_id' in request.session:
        month_name = mn
        months = list(calendar.month_name).index(month_name) 
        month = months - 1

        year = yr
    
        sid = request.session['s_id']
        loginn = Fin_Login_Details.objects.get(id=sid)
        if loginn.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = sid)
            events = Holiday.objects.filter(start_date__month=months,start_date__year=year,company_id=com.id)
            attendance = Fin_Attendances.objects.filter(employee = id,company = com.id,start_date__month=months,start_date__year =year)
            emp =Employee.objects.get(id=id)
        
        elif loginn.User_Type == 'Staff' :
            com = Fin_Staff_Details.objects.get(Login_Id = sid)
            events = Holiday.objects.filter(start_date__month=months,start_date__year=year,company_id=com.company_id)
            attendance = Fin_Attendances.objects.filter(employee = id,company = com.company_id,start_date__month=months,start_date__year =year)
            emp =Employee.objects.get(id=id)

        return render(request,'company/Fin_AttendanceView.html',{'events':events,'month':month,'year':year,'attendance':attendance,'emp':emp,'month_name':month_name})




def Fin_editAttendance(request,id,mn,yr,pk):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        log = Fin_Login_Details.objects.get(id = s_id)
        leave = Fin_Attendances.objects.get(id=id)
    
        if log.User_Type == 'Staff':
            staff =Fin_Staff_Details.objects.get(Login_Id =log)
            allmodules = Fin_Modules_List.objects.get(company_id = staff.company_id)
            emp = Employee.objects.filter(company = staff.company_id,employee_status = 'active')
            bgroup = Employee_Blood_Group.objects.filter(company = staff.company_id)
            if request.method == 'POST':
                emp = request.POST['emp']
                empid = Employee.objects.get(id = emp)
                leave.employee = empid
                leave.start_date = request.POST['sdate']
                leave.end_date = request.POST['edate']
                leave.reason = request.POST['reason']
                leave.status = request.POST['status']
                leave.save()
                att_history = Fin_Attendance_history(company = staff.company_id,login_id = log,attendance = leave,action = "Edited")
                att_history.save()
                return redirect('Fin_Attendanceview',mn,yr,pk)
        if log.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = log)
            allmodules = Fin_Modules_List.objects.get(company_id = com.id)
            emp = Employee.objects.filter(company = com.id,employee_status = 'active')
            bgroup = Employee_Blood_Group.objects.filter(company = com.id)
            if request.method == 'POST':
                emp = request.POST['emp']
                empid = Employee.objects.get(id = emp)
                leave.employee = empid
                leave.start_date = request.POST['sdate']
                leave.end_date = request.POST['edate']
                leave.reason = request.POST['reason']
                leave.status = request.POST['status']
                leave.save()
                att_history = Fin_Attendance_history(company = com,login_id = log,attendance = leave,action = "Edited")
                att_history.save()
                return redirect('Fin_Attendanceview',mn,yr,pk)
            
        context ={
            'emp':emp,'bloodgroup':bgroup,'leave':leave,'allmodules':allmodules
        }
        return render(request,'company/Fin_attendanceEdit.html',context)

def Fin_deleteAttendance(request,id,mn,yr,pk):
    month_name = mn
    year = yr
    leave = Fin_Attendances.objects.get(id = id)
    leave.delete()
    return redirect('Fin_Attendanceview',month_name,year,pk)




def Fin_attendance_history(request):
    hid = request.GET.get('hid')
    
    if 's_id' in request.session:
        s_id = request.session['s_id']
        log = Fin_Login_Details.objects.get(id = s_id)
        if log.User_Type == 'Staff':
            staff =Fin_Staff_Details.objects.get(Login_Id =log)
            exists = Fin_Attendance_history.objects.filter(company = staff.company_id,attendance = hid)
            data = [{'action': item.action, 'date': item.date, 'first_name': item.login_id.First_name, 'last_name': item.login_id.Last_name} for item in exists]
        if log.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = log)
            exists = Fin_Attendance_history.objects.filter(company = com.id,attendance = hid)
            data = [{'action': item.action, 'date': item.date, 'first_name': item.login_id.First_name, 'last_name': item.login_id.Last_name} for item in exists]

        return JsonResponse({'data': data})
    





def Fin_addcommentstoleave(request,id,mn,yr,pk):
    month_name = mn
    year = yr
    data = Fin_Attendances.objects.get(id=id)
    if 's_id' in request.session:
        if request.method == 'POST':
            s_id = request.session['s_id']
            log = Fin_Login_Details.objects.get(id = s_id)
            if log.User_Type == 'Staff':
                staff =Fin_Staff_Details.objects.get(Login_Id =log)
                comment = Fin_attendance_comment(company = staff.company_id, login_id = log, attendance = data, comment = request.POST['comment'])
                comment.save()
            if log.User_Type == 'Company':
                com = Fin_Company_Details.objects.get(Login_Id = log)
                comment = Fin_attendance_comment(company = com, login_id = log, attendance = data, comment = request.POST['comment'])
                comment.save()
            return redirect('Fin_Attendanceview',month_name,year,pk)
        return redirect('Fin_Attendanceview',month_name,year,pk)


def Fin_attendancecomments(request):
    hid = request.GET.get('hid')
    
    if 's_id' in request.session:
        s_id = request.session['s_id']
        log = Fin_Login_Details.objects.get(id = s_id)
        if log.User_Type == 'Staff':
            staff =Fin_Staff_Details.objects.get(Login_Id =log)
            exists = Fin_attendance_comment.objects.filter(company = staff.company_id,attendance = hid)
            data = [{'action': item.comment} for item in exists]
        if log.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = log)
            exists = Fin_attendance_comment.objects.filter(company = com.id,attendance = hid)
            data = [{'action': item.comment} for item in exists]
        return JsonResponse({'data': data})




def Fin_shareLeaveStatementToEmail(request,id,mn,yr):
    if 's_id' in request.session:
      
        if request.method == 'POST':
            emails_string = request.POST['email_ids']

            # Split the string by commas and remove any leading or trailing whitespace
            emails_list = [email.strip() for email in emails_string.split(',')]
            email_message = request.POST['email_message']
            # print(emails_list)
            month_name = mn
            months = list(calendar.month_name).index(month_name) 

            year = yr
            s_id = request.session['s_id']
            log = Fin_Login_Details.objects.get(id = s_id)
            emp = Employee.objects.get(id =id)

            if log.User_Type == 'Staff':
                staff =Fin_Staff_Details.objects.get(Login_Id =log)
                att = Fin_Attendances.objects.filter(employee = id,company = staff.company_id,start_date__month=months,start_date__year =year)
                context = {'att': att, 'emp': emp ,'month_name':month_name, 'year':year}
            if log.User_Type == 'Company':
                com = Fin_Company_Details.objects.get(Login_Id = log)
                att = Fin_Attendances.objects.filter(employee = id,company = com.id,start_date__month=months,start_date__year =year)
                context = {'att': att, 'emp': emp,'month_name':month_name, 'year':year}
            template_path = 'company/FIn_LeaveTransaction.html'
            template = get_template(template_path)

            html  = template.render(context)
            result = BytesIO()
            pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)#, link_callback=fetch_resources)
            pdf = result.getvalue()
            filename = f'Leave Statement - {emp.first_name} {emp.last_name}-{month_name},{year}.pdf'
            subject = f"Leave Statement - {emp.first_name} {emp.last_name}-{month_name},{year}"
            email = EmailMessage(subject, f"Hi,\nPlease find the attached Leave Statement - of-{emp.first_name} {emp.last_name}. \n{email_message}", from_email=settings.EMAIL_HOST_USER,to=emails_list)
            email.attach(filename, pdf, "application/pdf")
            email.send(fail_silently=False)

            msg = messages.success(request, 'Bill has been shared via email successfully..!')
            return redirect('Fin_Attendanceview',month_name,year,id)
            
#Antony_______________________

def Fin_edit_bank_trans(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')
        # banknew=Fin_BankTransactions.objects.get(id=id)
        bank=Fin_BankTransactions.objects.get(id=id)
        try:
            banks = Fin_BankTransactions.objects.get(id=bank.bank_to_bank)
        except:
            banks = None
        all_banks = Fin_Banking.objects.filter(company = company)
        print(all_banks)
    context = {
            'login_det':login_det,
            'cmp1':com,
            'allmodules':allmodules,
            'bank':bank,
            'banks':banks,
            'all_banks':all_banks,
            
        }  
    return render(request,'company/banking/Fin_edit_bank_trans.html',context)

def Fin_edit_bank_to_cash(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        if request.method == 'POST':
            f_bank = request.POST.get('bank')
            amount = request.POST.get('amount')
            adj_date = request.POST.get('adjdate')
            desc = request.POST.get('desc')

            
            transaction = Fin_BankTransactions.objects.get(id=id)
            bank = Fin_Banking.objects.get(id=f_bank)
            bank.current_balance = bank.current_balance -(int(amount) - transaction.amount)
            bank.save()
            
            transaction.banking.bank_name = f_bank
            transaction.amount=amount
            transaction.description=desc
            transaction.adjustment_date=adj_date
            transaction.current_balance= bank.current_balance               
           
            transaction.save()
            transaction_history = Fin_BankTransactionHistory(
                login_details = login_det,
                company = company,
                bank_transaction = transaction,
                action = 'Updated'
            )
            transaction_history.save()
            
        return redirect('Fin_view_bank',bank.id)


def Fin_edit_cash_to_bank(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        if request.method == 'POST':
            f_bank = request.POST.get('bank')
            amount = request.POST.get('amount')
            adj_date = request.POST.get('adjdate')
            desc = request.POST.get('desc')

            
            transaction = Fin_BankTransactions.objects.get(id=id)
            bank = Fin_Banking.objects.get(id=f_bank)
            bank.current_balance = bank.current_balance + (int(amount) - transaction.amount)
            bank.save()
            
            transaction.banking.bank_name = f_bank
            transaction.amount=amount
            transaction.description=desc
            transaction.adjustment_date=adj_date
            transaction.current_balance= bank.current_balance               
           
            transaction.save()
            transaction_history = Fin_BankTransactionHistory(
                login_details = login_det,
                company = company,
                bank_transaction = transaction,
                action = 'Updated'
            )
            transaction_history.save()
            
        return redirect('Fin_view_bank',bank.id)
    

def Fin_edit_bank_adjust(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id
        transaction = Fin_BankTransactions.objects.get(id=id)
        if request.method == 'POST':
            f_bank = request.POST.get('bank')
            type = request.POST.get('typ')
            amount = request.POST.get('amount')
            adj_date = request.POST.get('adjdate')
            desc = request.POST.get('desc')

            
            bank = Fin_Banking.objects.get(id=f_bank)
            if type == 'Increase Balance':
                bank.current_balance = bank.current_balance + (int(amount) - transaction.amount)
                bank.save()
            else:
                bank.current_balance = bank.current_balance - (int(amount) - transaction.amount)
                bank.save()
                    
            transaction.banking.bank_name = f_bank
            transaction.amount=amount
            transaction.adjustment_type=type
            transaction.description=desc
            transaction.adjustment_date=adj_date
            transaction.current_balance= bank.current_balance               
           
            transaction.save()
            transaction_history = Fin_BankTransactionHistory(
                login_details = login_det,
                company = company,
                bank_transaction = transaction,
                action = 'Updated'
            )
            transaction_history.save()
            
        return redirect('Fin_view_bank',bank.id)

def Fin_edit_bank_to_bank(request, transfer_id):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id
    if request.method == 'POST':
        fbank_id = request.POST.get('fbank')
        tbank_id = request.POST.get('tbank')

        transfer = Fin_BankTransactions.objects.get(id=transfer_id)
        transfer_to = Fin_BankTransactions.objects.get(id=transfer.bank_to_bank)
        old_amt = transfer_to.amount
        old_bank = Fin_Banking.objects.get(id = transfer.banking.id) if transfer.transaction_type == 'To Bank Transfer' else Fin_Banking.objects.get(id = transfer_to.banking.id)
        fbank = Fin_Banking.objects.get(id=fbank_id)
        tbank = Fin_Banking.objects.get(id=tbank_id)

        if tbank_id != old_bank:
            old_bank.current_balance -= old_amt
            old_bank.save()

        amount = request.POST.get('amount')

        adj_date = request.POST.get('adjdate')
        desc = request.POST.get('desc')

        # Update the balances of the banking accounts
        current_balance = transfer.current_balance
        current_balance_trans_to = transfer_to.current_balance
        current_balance_fm = fbank.current_balance
        current_balance_to = tbank.current_balance


        if transfer.transaction_type == 'To Bank Transfer':
            if int(amount) > int(transfer.amount):
                fbank.current_balance -= (int(amount) - int(transfer.amount))
                tbank.current_balance += (int(amount) - int(transfer.amount))
                transfer.current_balance += (int(amount) - int(transfer.amount))
                transfer_to.current_balance -= (int(amount) - int(transfer.amount))

            elif int(amount) < int(transfer.amount):
                fbank.current_balance += (int(transfer.amount) - int(amount))
                tbank.current_balance -= (int(transfer.amount)  - int(amount))
                transfer.current_balance -= (int(transfer.amount)  - int(amount))
                transfer_to.current_balance += (int(transfer.amount)  - int(amount))

            else:
                fbank.current_balance = current_balance_fm
                tbank.current_balance = current_balance_to
                transfer.current_balance = current_balance
                transfer_to.current_balance = current_balance_trans_to

        elif transfer.transaction_type == 'From Bank Transfer':
            if int(amount) > int(transfer.amount):
                fbank.current_balance -= (int(amount) - int(transfer.amount))
                tbank.current_balance += (int(amount) - int(transfer.amount))
                transfer.current_balance -= (int(amount) - int(transfer.amount))
                transfer_to.current_balance += (int(amount) - int(transfer.amount))

            elif int(amount) < int(transfer.amount):
                fbank.current_balance += (int(transfer.amount) - int(amount))
                tbank.current_balance -= (int(transfer.amount) - int(amount))
                transfer.current_balance += (int(transfer.amount) - int(amount))
                transfer_to.current_balance -= (int(transfer.amount) - int(amount))

            else:
                fbank.current_balance = current_balance_fm
                tbank.current_balance = current_balance_to
                transfer.current_balance = current_balance
                transfer_to.current_balance = current_balance_trans_to


        if transfer.transaction_type == 'To Bank Transfer':
            transfer.from_type = 'From : ' + fbank.bank_name
            transfer.to_type = ' To : ' + tbank.bank_name
            transfer.banking=tbank
            transfer_to.from_type = 'From : ' + fbank.bank_name
            transfer_to.to_type = ' To : ' + tbank.bank_name
            transfer_to.banking=fbank
            if tbank_id != transfer_to.banking:  # Check if the destination bank has changed
            # Adjust balances for the old and new banks
                transfer.banking.current_balance += int(amount)
                transfer.save()
                tbank.save()
                tbank.current_balance == transfer_to.current_balance
        elif transfer.transaction_type == 'From Bank Transfer':
            transfer.from_type = 'From : ' + fbank.bank_name
            transfer.to_type = ' To : ' + tbank.bank_name
            transfer.banking=fbank
            transfer_to.from_type = 'From : ' + fbank.bank_name
            transfer_to.to_type = ' To : ' + tbank.bank_name
            transfer_to.banking=tbank
            # Before saving the changes to transfer and transfer_to
            if tbank_id != transfer_to.banking:  # Check if the destination bank has changed
            # Adjust balances for the old and new banks
                transfer_to.banking.current_balance += int(amount)
                transfer_to.save()
                tbank.save()
                tbank.current_balance == transfer_to.current_balance

            
        
        transfer.amount = amount
        transfer.adjustment_date = adj_date
        transfer.description = desc
        transfer_to.amount = amount
        transfer_to.adjustment_date = adj_date
        transfer_to.description = desc
        
        fbank.save()
        tbank.save()
        transfer.save()
        transfer_to.save()

        

        transaction_history = Fin_BankTransactionHistory(
                login_details = login_det,
                company = company,
                bank_transaction = transfer,
                action = 'Updated'
            )
        transaction_history.save()

        return redirect('Fin_banking_listout')
    

    
def Fin_bank_transcation_history(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        bank=Fin_BankTransactionHistory.objects.filter(bank_transaction = id)
        all_banks = Fin_Banking.objects.filter(company = company)

        context = {
                'login_det':login_det,
                'com':com,
                'allmodules':allmodules,
                'bank':bank,
                'all_banks':all_banks,
               
            }  
       
        return render(request,'company/banking/Fin_bank_transcation_history.html',context)
    

def Fin_bank_transaction_delete(request,id):
  transaction = Fin_BankTransactions.objects.get(id=id)
  bank = Fin_Banking.objects.get(id=transaction.banking_id)
  transfer_to = Fin_BankTransactions.objects.get(id=transaction.bank_to_bank)
  bank_to = Fin_Banking.objects.get(id=transfer_to.banking_id)


  if transaction.transaction_type=='Cash Withdraw':
    bank.current_balance = bank.current_balance + transaction.amount
  elif transaction.transaction_type=='Cash Deposit':
    bank.current_balance = bank.current_balance - transaction.amount
  elif transaction.adjustment_type=='Reduce Balance':
    bank.current_balance = bank.current_balance + transaction.amount
  elif transaction.adjustment_type=='Increase Balance':
    bank.current_balance = bank.current_balance - transaction.amount
  elif transaction.transaction_type=='From Bank Transfer':
    bank.current_balance = bank.current_balance + transaction.amount
    bank_to.current_balance = bank_to.current_balance - transfer_to.amount
  elif transaction.transaction_type=='To Bank Transfer':
    bank.current_balance = bank.current_balance - transaction.amount
    bank_to.current_balance = bank_to.current_balance + transfer_to.amount
  else:
    bank.current_balance = bank.current_balance - transaction.amount
  bank.save()
  bank_to.save()
  transaction.delete()
  transfer_to.delete()
  return redirect('Fin_banking_listout')            
  
  
# < ------------- Shemeem -------- > Purchase Order < ------------------------------- >
        
def Fin_purchaseOrder(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            cmp = com
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            cmp = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = cmp, status = 'New')
        purchaseOrders = Fin_Purchase_Order.objects.filter(Company = cmp)
        return render(request,'company/Fin_Purchase_Order.html',{'allmodules':allmodules,'com':com, 'cmp':cmp,'data':data,'purchase_orders':purchaseOrders})
    else:
       return redirect('/')

def Fin_addPurchaseOrder(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            cmp = com
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            cmp = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = cmp, status = 'New')
        cust = Fin_Customers.objects.filter(Company = cmp, status = 'Active')
        vend = Fin_Vendors.objects.filter(Company = cmp, status = 'Active')
        itms = Fin_Items.objects.filter(Company = cmp, status = 'Active')
        trms = Fin_Company_Payment_Terms.objects.filter(Company = cmp)
        bnk = Fin_Banking.objects.filter(company = cmp)
        lst = Fin_Price_List.objects.filter(Company = cmp, status = 'Active')
        units = Fin_Units.objects.filter(Company = cmp)
        acc = Fin_Chart_Of_Account.objects.filter(Q(account_type='Expense') | Q(account_type='Other Expense') | Q(account_type='Cost Of Goods Sold'), Company=cmp).order_by('account_name')

        # Fetching last pur. order and assigning upcoming ref no as current + 1
        # Also check for if any bill is deleted and ref no is continuos w r t the deleted pur. order
        latest_po = Fin_Purchase_Order.objects.filter(Company = cmp).order_by('-id').first()

        new_number = int(latest_po.reference_no) + 1 if latest_po else 1

        if Fin_Purchase_Order_Reference.objects.filter(Company = cmp).exists():
            deleted = Fin_Purchase_Order_Reference.objects.get(Company = cmp)
            
            if deleted:
                while int(deleted.reference_no) >= new_number:
                    new_number+=1

        # Finding next PO number w r t last PO number if exists.
        nxtPO = ""
        lastPO = Fin_Purchase_Order.objects.filter(Company = cmp).last()
        if lastPO:
            purchaseOrder_no = str(lastPO.purchase_order_no)
            numbers = []
            stri = []
            for word in purchaseOrder_no:
                if word.isdigit():
                    numbers.append(word)
                else:
                    stri.append(word)
            
            num=''
            for i in numbers:
                num +=i
            
            st = ''
            for j in stri:
                st = st+j

            p_order_num = int(num)+1

            if num[0] == '0':
                if p_order_num <10:
                    nxtPO = st+'0'+ str(p_order_num)
                else:
                    nxtPO = st+ str(p_order_num)
            else:
                nxtPO = st+ str(p_order_num)
        else:
            nxtPO = 'PO01'

        context = {
            'allmodules':allmodules, 'com':com, 'cmp':cmp, 'data':data, 'customers':cust, 'vendors':vend, 'items':itms, 'pTerms':trms,'list':lst,
            'ref_no':new_number,'banks':bnk,'PONo':nxtPO,'units':units, 'accounts':acc
        }
        return render(request,'company/Fin_Add_Purchase_Order.html',context)
    else:
       return redirect('/')

def Fin_getVendorData(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
        
        vndId = request.POST['id']
        vend = Fin_Vendors.objects.get(id = vndId)

        if vend:
            context = {
                'status':True, 'id':vend.id, 'email':vend.email, 'gstType':vend.gst_type,'shipState':vend.place_of_supply,'gstin':False if vend.gstin == "" or vend.gstin == None else True, 'gstNo':vend.gstin,
                'street':vend.billing_street, 'city':vend.billing_city, 'state':vend.billing_state, 'country':vend.billing_country, 'pincode':vend.billing_pincode
            }
            return JsonResponse(context)
        else:
            return JsonResponse({'status':False, 'message':'Something went wrong..!'})
    else:
       return redirect('/')

def Fin_checkPurchaseOrderNumber(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        PurOrdNo = request.GET['PONum']

        # Finding next pur_order number w r t last pur_order number if exists.
        nxtPO = ""
        lastPO = Fin_Purchase_Order.objects.filter(Company = com).last()
        if lastPO:
            po_no = str(lastPO.purchase_order_no)
            numbers = []
            stri = []
            for word in po_no:
                if word.isdigit():
                    numbers.append(word)
                else:
                    stri.append(word)
            
            num=''
            for i in numbers:
                num +=i
            
            st = ''
            for j in stri:
                st = st+j

            p_order_num = int(num)+1

            if num[0] == '0':
                if p_order_num <10:
                    nxtPO = st+'0'+ str(p_order_num)
                else:
                    nxtPO = st+ str(p_order_num)
            else:
                nxtPO = st+ str(p_order_num)

        PatternStr = []
        for word in PurOrdNo:
            if word.isdigit():
                pass
            else:
                PatternStr.append(word)
        
        pattern = ''
        for j in PatternStr:
            pattern += j

        pattern_exists = checkPurchaseOrderNumberPattern(pattern)

        if pattern !="" and pattern_exists:
            return JsonResponse({'status':False, 'message':'Pur. Order No. Pattern already Exists.!'})
        elif Fin_Purchase_Order.objects.filter(Company = com, purchase_order_no__iexact = PurOrdNo).exists():
            return JsonResponse({'status':False, 'message':'Pur. Order No. already Exists.!'})
        elif nxtPO != "" and PurOrdNo != nxtPO:
            return JsonResponse({'status':False, 'message':'Pur. Order No. is not continuous.!'})
        else:
            return JsonResponse({'status':True, 'message':'Number is okay.!'})
    else:
       return redirect('/')

def checkPurchaseOrderNumberPattern(pattern):
    models = [Fin_Invoice, Fin_Sales_Order, Fin_Estimate, Fin_Purchase_Bill, Fin_Manual_Journal, Fin_Recurring_Invoice]

    for model in models:
        field_name = model.getNumFieldName(model)
        if model.objects.filter(**{f"{field_name}__icontains": pattern}).exists():
            return True
    return False

def Fin_createPurchaseOrder(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        if request.method == 'POST':
            PONum = request.POST['purchase_order_no']
            if Fin_Purchase_Order.objects.filter(Company = com, purchase_order_no__iexact = PONum).exists():
                res = f'<script>alert("Purchase Order Number `{PONum}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)

            POrder = Fin_Purchase_Order(
                Company = com,
                LoginDetails = com.Login_Id,
                Vendor = None if request.POST['vendorId'] == "" else Fin_Vendors.objects.get(id = request.POST['vendorId']),
                vendor_email = request.POST['vendorEmail'],
                vendor_address = request.POST['vendor_bill_address'],
                vendor_gst_type = request.POST['vendor_gst_type'],
                vendor_gstin = request.POST['vendor_gstin'],
                vendor_source_of_supply = request.POST['source_of_supply'],

                Customer = None if request.POST['customerId'] == "" else Fin_Customers.objects.get(id = request.POST['customerId']),
                customer_name = request.POST['customer'],
                customer_email = request.POST['customerEmail'],
                customer_address = request.POST['bill_address'],
                customer_gst_type = request.POST['gst_type'],
                customer_gstin = request.POST['gstin'],
                customer_place_of_supply = request.POST['place_of_supply'],

                reference_no = request.POST['reference_number'],
                purchase_order_no = PONum,
                payment_terms = Fin_Company_Payment_Terms.objects.get(id = request.POST['payment_term']),
                purchase_order_date = request.POST['purchase_order_date'],
                due_date = datetime.strptime(request.POST['due_date'], '%d-%m-%Y').date(),
                payment_method = None if request.POST['payment_method'] == "" else request.POST['payment_method'],
                cheque_no = None if request.POST['cheque_id'] == "" else request.POST['cheque_id'],
                upi_no = None if request.POST['upi_id'] == "" else request.POST['upi_id'],
                bank_acc_no = None if request.POST['bnk_id'] == "" else request.POST['bnk_id'],
                subtotal = 0.0 if request.POST['subtotal'] == "" else float(request.POST['subtotal']),
                igst = 0.0 if request.POST['igst'] == "" else float(request.POST['igst']),
                cgst = 0.0 if request.POST['cgst'] == "" else float(request.POST['cgst']),
                sgst = 0.0 if request.POST['sgst'] == "" else float(request.POST['sgst']),
                tax_amount = 0.0 if request.POST['taxamount'] == "" else float(request.POST['taxamount']),
                adjustment = 0.0 if request.POST['adj'] == "" else float(request.POST['adj']),
                shipping_charge = 0.0 if request.POST['ship'] == "" else float(request.POST['ship']),
                grandtotal = 0.0 if request.POST['grandtotal'] == "" else float(request.POST['grandtotal']),
                paid_off = 0.0 if request.POST['advance'] == "" else float(request.POST['advance']),
                balance = request.POST['grandtotal'] if request.POST['balance'] == "" else float(request.POST['balance']),
                note = request.POST['note']
            )

            POrder.save()

            if len(request.FILES) != 0:
                POrder.file=request.FILES.get('file')
            POrder.save()

            if 'Draft' in request.POST:
                POrder.status = "Draft"
            elif "Save" in request.POST:
                POrder.status = "Saved" 
            POrder.save()

            # Save Sales Order items.

            itemId = request.POST.getlist("item_id[]")
            itemName = request.POST.getlist("item_name[]")
            hsn  = request.POST.getlist("hsn[]")
            qty = request.POST.getlist("qty[]")
            price = request.POST.getlist("price[]")
            tax = request.POST.getlist("taxGST[]") if request.POST['source_of_supply'] == com.State else request.POST.getlist("taxIGST[]")
            discount = request.POST.getlist("discount[]")
            total = request.POST.getlist("total[]")

            if len(itemId)==len(itemName)==len(hsn)==len(qty)==len(price)==len(tax)==len(discount)==len(total) and itemId and itemName and hsn and qty and price and tax and discount and total:
                mapped = zip(itemId,itemName,hsn,qty,price,tax,discount,total)
                mapped = list(mapped)
                for ele in mapped:
                    itm = Fin_Items.objects.get(id = int(ele[0]))
                    Fin_Purchase_Order_Items.objects.create(PurchaseOrder = POrder, Item = itm, hsn = ele[2], quantity = int(ele[3]), price = float(ele[4]), tax = ele[5], discount = float(ele[6]), total = float(ele[7]))
                    # itm.current_stock -= int(ele[3])
                    # itm.save()
            
            # Save transaction
                    
            Fin_Purchase_Order_History.objects.create(
                Company = com,
                LoginDetails = data,
                PurchaseOrder = POrder,
                action = 'Created'
            )

            return redirect(Fin_purchaseOrder)
        else:
            return redirect(Fin_addPurchaseOrder)
    else:
       return redirect('/')

def Fin_viewPurchaseOrder(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)

        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            cmp = com

        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            cmp = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = cmp,status = 'New')
        purchaseOrder = Fin_Purchase_Order.objects.get(id = id)
        cmt = Fin_Purchase_Order_Comments.objects.filter(PurchaseOrder = purchaseOrder)
        hist = Fin_Purchase_Order_History.objects.filter(PurchaseOrder = purchaseOrder).last()
        POItems = Fin_Purchase_Order_Items.objects.filter(PurchaseOrder = purchaseOrder)
        try:
            created = Fin_Purchase_Order_History.objects.get(PurchaseOrder = purchaseOrder, action = 'Created')
        except:
            created = None
        
        return render(request,'company/Fin_View_Purchase_Order.html',{'allmodules':allmodules,'com':com,'cmp':cmp, 'data':data, 'order':purchaseOrder,'orderItems':POItems, 'history':hist, 'comments':cmt, 'created':created})
    else:
       return redirect('/')

def Fin_convertPurchaseOrder(request,id):
    if 's_id' in request.session:

        pOrder = Fin_Purchase_Order.objects.get(id = id)
        pOrder.status = 'Saved'
        pOrder.save()
        return redirect(Fin_viewPurchaseOrder, id)

def Fin_addPurchaseOrderComment(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        pOrder = Fin_Purchase_Order.objects.get(id = id)
        if request.method == "POST":
            cmt = request.POST['comment'].strip()

            Fin_Purchase_Order_Comments.objects.create(Company = com, PurchaseOrder = pOrder, comments = cmt)
            return redirect(Fin_viewPurchaseOrder, id)
        return redirect(Fin_viewPurchaseOrder, id)
    return redirect('/')

def Fin_deletePurchaseOrderComment(request,id):
    if 's_id' in request.session:
        cmt = Fin_Purchase_Order_Comments.objects.get(id = id)
        orderId = cmt.PurchaseOrder.id
        cmt.delete()
        return redirect(Fin_viewPurchaseOrder, orderId)
    
def Fin_purchaseOrderHistory(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        pOrder = Fin_Purchase_Order.objects.get(id = id)
        his = Fin_Purchase_Order_History.objects.filter(PurchaseOrder = pOrder)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
        
        return render(request,'company/Fin_Purchase_Order_History.html',{'allmodules':allmodules,'com':com,'data':data,'history':his, 'order':pOrder})
    else:
       return redirect('/')
    
def Fin_deletePurchaseOrder(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        pOrder = Fin_Purchase_Order.objects.get( id = id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        Fin_Purchase_Order_Items.objects.filter(PurchaseOrder = pOrder).delete()

        # Storing ref number to deleted table
        # if entry exists and lesser than the current, update and save => Only one entry per company
        if Fin_Purchase_Order_Reference.objects.filter(Company = com).exists():
            deleted = Fin_Purchase_Order_Reference.objects.get(Company = com)
            if int(pOrder.reference_no) > int(deleted.reference_no):
                deleted.reference_no = pOrder.reference_no
                deleted.save()
        else:
            Fin_Purchase_Order_Reference.objects.create(Company = com, reference_no = pOrder.reference_no, LoginDetails = com.Login_Id)
        
        pOrder.delete()
        return redirect(Fin_purchaseOrder)

def Fin_attachPurchaseOrderFile(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        pOrder = Fin_Purchase_Order.objects.get(id = id)

        if request.method == 'POST' and len(request.FILES) != 0:
            pOrder.file = request.FILES.get('file')
            pOrder.save()

        return redirect(Fin_viewPurchaseOrder, id)
    else:
        return redirect('/')

def Fin_purchaseOrderPdf(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        pOrder = Fin_Purchase_Order.objects.get(id = id)
        itms = Fin_Purchase_Order_Items.objects.filter(PurchaseOrder = pOrder)
    
        context = {'order':pOrder, 'orderItems':itms,'cmp':com}
        
        template_path = 'company/Fin_Purchase_Order_Pdf.html'
        fname = 'Purchase_Order_'+pOrder.purchase_order_no
        # return render(request, 'company/Fin_Invoice_Pdf.html',context)
        # Create a Django response object, and specify content_type as pdftemp_
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] =f'attachment; filename = {fname}.pdf'
        # find the template and render it.
        template = get_template(template_path)
        html = template.render(context)

        # create a pdf
        pisa_status = pisa.CreatePDF(
        html, dest=response)
        # if error then show some funny view
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
    else:
        return redirect('/')

def Fin_sharePurchaseOrderToEmail(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        pOrder = Fin_Purchase_Order.objects.get(id = id)
        itms = Fin_Purchase_Order_Items.objects.filter(PurchaseOrder = pOrder)
        try:
            if request.method == 'POST':
                emails_string = request.POST['email_ids']

                # Split the string by commas and remove any leading or trailing whitespace
                emails_list = [email.strip() for email in emails_string.split(',')]
                email_message = request.POST['email_message']
                # print(emails_list)
            
                context = {'order':pOrder, 'orderItems':itms,'cmp':com}
                template_path = 'company/Fin_Purchase_Order_Pdf.html'
                template = get_template(template_path)

                html  = template.render(context)
                result = BytesIO()
                pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
                pdf = result.getvalue()
                filename = f'Purchase_Order_{pOrder.purchase_order_no}'
                subject = f"Purchase_Order_{pOrder.purchase_order_no}"
                email = EmailMessage(subject, f"Hi,\nPlease find the attached Purchase Order for - #-{pOrder.purchase_order_no}. \n{email_message}\n\n--\nRegards,\n{com.Company_name}\n{com.Address}\n{com.State} - {com.Country}\n{com.Contact}", from_email=settings.EMAIL_HOST_USER, to=emails_list)
                email.attach(filename, pdf, "application/pdf")
                email.send(fail_silently=False)

                messages.success(request, 'Purchase Order details has been shared via email successfully..!')
                return redirect(Fin_viewPurchaseOrder,id)
        except Exception as e:
            print(e)
            messages.error(request, f'{e}')
            return redirect(Fin_viewPurchaseOrder, id)

def Fin_createVendorAjax(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        fName = request.POST['first_name']
        lName = request.POST['last_name']
        gstIn = request.POST['gstin']
        pan = request.POST['pan_no']
        email = request.POST['email']
        phn = request.POST['mobile']

        if Fin_Vendors.objects.filter(Company = com, first_name__iexact = fName, last_name__iexact = lName).exists():
            res = f"Vendor `{fName} {lName}` already exists, try another!"
            return JsonResponse({'status': False, 'message':res})
        elif gstIn != "" and Fin_Vendors.objects.filter(Company = com, gstin__iexact = gstIn).exists():
            res = f"GSTIN `{gstIn}` already exists, try another!"
            return JsonResponse({'status': False, 'message':res})
        elif Fin_Vendors.objects.filter(Company = com, pan_no__iexact = pan).exists():
            res = f"PAN No `{pan}` already exists, try another!"
            return JsonResponse({'status': False, 'message':res})
        elif Fin_Vendors.objects.filter(Company = com, mobile__iexact = phn).exists():
            res = f"Phone Number `{phn}` already exists, try another!"
            return JsonResponse({'status': False, 'message':res})
        elif Fin_Vendors.objects.filter(Company = com, email__iexact = email).exists():
            res = f"Email `{email}` already exists, try another!"
            return JsonResponse({'status': False, 'message':res})

        vnd = Fin_Vendors(
            Company = com,
            LoginDetails = com.Login_Id,
            title = request.POST['title'],
            first_name = fName,
            last_name = lName,
            company = request.POST['company_name'],
            location = request.POST['location'],
            place_of_supply = request.POST['place_of_supply'],
            gst_type = request.POST['gst_type'],
            gstin = None if request.POST['gst_type'] == "Unregistered Business" or request.POST['gst_type'] == 'Overseas' or request.POST['gst_type'] == 'Consumer' else gstIn,
            pan_no = pan,
            email = email,
            mobile = phn,
            website = request.POST['website'],
            price_list = None if request.POST['price_list'] ==  "" else Fin_Price_List.objects.get(id = request.POST['price_list']),
            payment_terms = None if request.POST['payment_terms'] == "" else Fin_Company_Payment_Terms.objects.get(id = request.POST['payment_terms']),
            opening_balance = 0 if request.POST['open_balance'] == "" else float(request.POST['open_balance']),
            open_balance_type = request.POST['balance_type'],
            current_balance = 0 if request.POST['open_balance'] == "" else float(request.POST['open_balance']),
            credit_limit = 0 if request.POST['credit_limit'] == "" else abs(float(request.POST['credit_limit'])) * -1,
            currency = request.POST['currency'],
            billing_street = request.POST['street'],
            billing_city = request.POST['city'],
            billing_state = request.POST['state'],
            billing_pincode = request.POST['pincode'],
            billing_country = request.POST['country'],
            ship_street = request.POST['shipstreet'],
            ship_city = request.POST['shipcity'],
            ship_state = request.POST['shipstate'],
            ship_pincode = request.POST['shippincode'],
            ship_country = request.POST['shipcountry'],
            status = 'Active'
        )
        vnd.save()

        #save transaction

        Fin_Vendor_History.objects.create(
            Company = com,
            LoginDetails = data,
            Vendor = vnd,
            action = 'Created'
        )

        return JsonResponse({'status': True})
    
    else:
        return redirect('/')
    
def Fin_getVendors(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        options = {}
        option_objects = Fin_Vendors.objects.filter(Company = com, status = 'Active')
        for option in option_objects:
            options[option.id] = [option.id , option.title, option.first_name, option.last_name]

        return JsonResponse(options)
    else:
        return redirect('/')

def Fin_editPurchaseOrder(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            cmp = com
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            cmp = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = cmp, status = 'New')
        pOrder = Fin_Purchase_Order.objects.get(id = id)
        POItms = Fin_Purchase_Order_Items.objects.filter(PurchaseOrder = pOrder)

        cust = Fin_Customers.objects.filter(Company = cmp, status = 'Active')
        vend = Fin_Vendors.objects.filter(Company = cmp, status = 'Active')
        itms = Fin_Items.objects.filter(Company = cmp, status = 'Active')
        trms = Fin_Company_Payment_Terms.objects.filter(Company = cmp)
        bnk = Fin_Banking.objects.filter(company = cmp)
        lst = Fin_Price_List.objects.filter(Company = cmp, status = 'Active')
        units = Fin_Units.objects.filter(Company = cmp)
        acc = Fin_Chart_Of_Account.objects.filter(Q(account_type='Expense') | Q(account_type='Other Expense') | Q(account_type='Cost Of Goods Sold'), Company=cmp).order_by('account_name')

        context = {
            'allmodules':allmodules, 'com':com, 'cmp':cmp, 'data':data,'order':pOrder, 'orderItems':POItms, 'customers':cust, 'items':itms, 'pTerms':trms,'list':lst,
            'banks':bnk,'units':units, 'accounts':acc, 'vendors':vend
        }
        return render(request,'company/Fin_Edit_Purchase_Order.html',context)
    else:
       return redirect('/')

def Fin_updatePurchaseOrder(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        pOrder = Fin_Purchase_Order.objects.get(id = id)
        if request.method == 'POST':
            PONum = request.POST['purchase_order_no']
            if pOrder.purchase_order_no != PONum and Fin_Purchase_Order.objects.filter(Company = com, purchase_order_no__iexact = PONum).exists():
                res = f'<script>alert("Purchase Order Number `{PONum}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)

            pOrder.Vendor = None if request.POST['vendorId'] == "" else Fin_Vendors.objects.get(id = request.POST['vendorId'])
            pOrder.vendor_email = request.POST['vendorEmail']
            pOrder.vendor_address = request.POST['vendor_bill_address']
            pOrder.vendor_gst_type = request.POST['vendor_gst_type']
            pOrder.vendor_gstin = request.POST['vendor_gstin']
            pOrder.vendor_source_of_supply = request.POST['source_of_supply']

            pOrder.Customer = None if request.POST['customerId'] == "" else Fin_Customers.objects.get(id = request.POST['customerId'])
            pOrder.customer_name = request.POST['customer']
            pOrder.customer_email = request.POST['customerEmail']
            pOrder.customer_address = request.POST['bill_address']
            pOrder.customer_gst_type = request.POST['gst_type']
            pOrder.customer_gstin = request.POST['gstin']
            pOrder.customer_place_of_supply = request.POST['place_of_supply']

            pOrder.reference_no = request.POST['reference_number']
            pOrder.purchase_order_no = PONum
            pOrder.payment_terms = Fin_Company_Payment_Terms.objects.get(id = request.POST['payment_term'])
            pOrder.purchase_order_date = request.POST['purchase_order_date']
            pOrder.due_date = datetime.strptime(request.POST['due_date'], '%d-%m-%Y').date()

            pOrder.payment_method = None if request.POST['payment_method'] == "" else request.POST['payment_method']
            pOrder.cheque_no = None if request.POST['cheque_id'] == "" else request.POST['cheque_id']
            pOrder.upi_no = None if request.POST['upi_id'] == "" else request.POST['upi_id']
            pOrder.bank_acc_no = None if request.POST['bnk_id'] == "" else request.POST['bnk_id']

            pOrder.subtotal = 0.0 if request.POST['subtotal'] == "" else float(request.POST['subtotal'])
            pOrder.igst = 0.0 if request.POST['igst'] == "" else float(request.POST['igst'])
            pOrder.cgst = 0.0 if request.POST['cgst'] == "" else float(request.POST['cgst'])
            pOrder.sgst = 0.0 if request.POST['sgst'] == "" else float(request.POST['sgst'])
            pOrder.tax_amount = 0.0 if request.POST['taxamount'] == "" else float(request.POST['taxamount'])
            pOrder.adjustment = 0.0 if request.POST['adj'] == "" else float(request.POST['adj'])
            pOrder.shipping_charge = 0.0 if request.POST['ship'] == "" else float(request.POST['ship'])
            pOrder.grandtotal = 0.0 if request.POST['grandtotal'] == "" else float(request.POST['grandtotal'])
            pOrder.paid_off = 0.0 if request.POST['advance'] == "" else float(request.POST['advance'])
            pOrder.balance = request.POST['grandtotal'] if request.POST['balance'] == "" else float(request.POST['balance'])
            
            pOrder.note = request.POST['note']

            if len(request.FILES) != 0:
                pOrder.file=request.FILES.get('file')

            pOrder.save()

            # Save Purchase order items.

            itemId = request.POST.getlist("item_id[]")
            itemName = request.POST.getlist("item_name[]")
            hsn  = request.POST.getlist("hsn[]")
            qty = request.POST.getlist("qty[]")
            price = request.POST.getlist("price[]")
            tax = request.POST.getlist("taxGST[]") if request.POST['source_of_supply'] == com.State else request.POST.getlist("taxIGST[]")
            discount = request.POST.getlist("discount[]")
            total = request.POST.getlist("total[]")
            po_item_ids = request.POST.getlist("id[]")
            POItem_ids = [int(id) for id in po_item_ids]

            order_items = Fin_Purchase_Order_Items.objects.filter(PurchaseOrder = pOrder)
            object_ids = [obj.id for obj in order_items]

            ids_to_delete = [obj_id for obj_id in object_ids if obj_id not in POItem_ids]

            Fin_Purchase_Order_Items.objects.filter(id__in=ids_to_delete).delete()
            
            count = Fin_Purchase_Order_Items.objects.filter(PurchaseOrder = pOrder).count()

            if len(itemId)==len(itemName)==len(hsn)==len(qty)==len(price)==len(tax)==len(discount)==len(total)==len(POItem_ids) and POItem_ids and itemId and itemName and hsn and qty and price and tax and discount and total:
                mapped = zip(itemId,itemName,hsn,qty,price,tax,discount,total,POItem_ids)
                mapped = list(mapped)
                for ele in mapped:
                    if int(len(itemId))>int(count):
                        if ele[8] == 0:
                            itm = Fin_Items.objects.get(id = int(ele[0]))
                            Fin_Purchase_Order_Items.objects.create(PurchaseOrder = pOrder, Item = itm, hsn = ele[2], quantity = int(ele[3]), price = float(ele[4]), tax = ele[5], discount = float(ele[6]), total = float(ele[7]))
                        else:
                            itm = Fin_Items.objects.get(id = int(ele[0]))
                            Fin_Purchase_Order_Items.objects.filter( id = int(ele[8])).update(PurchaseOrder = pOrder, Item = itm, hsn = ele[2], quantity = int(ele[3]), price = float(ele[4]), tax = ele[5], discount = float(ele[6]), total = float(ele[7]))
                    else:
                        itm = Fin_Items.objects.get(id = int(ele[0]))
                        Fin_Purchase_Order_Items.objects.filter( id = int(ele[8])).update(PurchaseOrder = pOrder, Item = itm, hsn = ele[2], quantity = int(ele[3]), price = float(ele[4]), tax = ele[5], discount = float(ele[6]), total = float(ele[7]))
            
            # Save transaction
                    
            Fin_Purchase_Order_History.objects.create(
                Company = com,
                LoginDetails = data,
                PurchaseOrder = pOrder,
                action = 'Edited'
            )

            return redirect(Fin_viewPurchaseOrder, id)
        else:
            return redirect(Fin_editPurchaseOrder, id)
    else:
       return redirect('/')

def Fin_convertPurchaseOrderToBill(request,id):
    s_id = request.session['s_id']
    data = Fin_Login_Details.objects.get(id = s_id)
    if data.User_Type == "Company":
        com = Fin_Company_Details.objects.get(Login_Id = s_id)
        cmp = com
    else:
        com = Fin_Staff_Details.objects.get(Login_Id = s_id)
        cmp = com.company_id

    allmodules = Fin_Modules_List.objects.get(company_id = cmp, status = 'New')

    ven = Fin_Vendors.objects.filter(Company = cmp, status = 'Active')
    cust = Fin_Customers.objects.filter(Company = cmp, status = 'Active')
    bnk = Fin_Banking.objects.filter(company = cmp, bank_status = 'Active')
    itm = Fin_Items.objects.filter(Company = cmp, status = 'Active')
    plist = Fin_Price_List.objects.filter(Company = cmp, type = 'Purchase', status = 'Active')
    terms = Fin_Company_Payment_Terms.objects.filter(Company = cmp)
    units = Fin_Units.objects.filter(Company = cmp)
    account = Fin_Chart_Of_Account.objects.filter(Q(account_type='Expense') | Q(account_type='Other Expense') | Q(account_type='Cost Of Goods Sold'), Company=cmp).order_by('account_name')
    tod = datetime.now().strftime('%Y-%m-%d')
    if Fin_Purchase_Bill.objects.filter(company = cmp):
        try:
            ref_no = int(Fin_Purchase_Bill_Ref_No.objects.filter(company = cmp).last().ref_no) + 1
        except:
            ref_no =  1
        bill_no = Fin_Purchase_Bill.objects.filter(company = cmp).last().bill_no
        match = re.search(r'^(\d+)|(\d+)$', bill_no)
        if match:
            numeric_part = match.group(0)
            incremented_numeric = str(int(numeric_part) + 1).zfill(len(numeric_part))
            bill_no = re.sub(r'\d+', incremented_numeric, bill_no, count=1)
    else:
        try:
            ref_no = int(Fin_Purchase_Bill_Ref_No.objects.filter(company = cmp).last().ref_no) + 1
        except:
            ref_no =  1
        bill_no = 1000

    pbill = Fin_Purchase_Order.objects.get(id = id)
    pitm = Fin_Purchase_Order_Items.objects.filter(PurchaseOrder = pbill)
    context = {
        'allmodules':allmodules, 'data':data, 'com':com, 'ven':ven, 'cust':cust, 'bnk':bnk, 'units':units,
        'account':account, 'itm':itm, 'tod':tod, 'plist':plist, 'ref_no': ref_no, 'bill_no':bill_no, 'terms':terms,
        'pbill':pbill, 'pitm':pitm
    }

    return render(request, 'company/Fin_Convert_PurchaseOrder_toBill.html', context)

def Fin_purchaseOrderConvertBill(request, id):
  if request.method == 'POST': 
    s_id = request.session['s_id']
    data = Fin_Login_Details.objects.get(id = s_id)
    if data.User_Type == "Company":
        com = Fin_Company_Details.objects.get(Login_Id = s_id)
    else:
        com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
    
    purchaseOrder = Fin_Purchase_Order.objects.get(id = id)

    ven = Fin_Vendors.objects.get(id = request.POST.get('ven_name'))
    if request.POST.get('cust_name') == "" or request.POST.get('cust_name') == 'none':
        cust = None
    else:
        cust = Fin_Customers.objects.get(id = request.POST.get('cust_name'))
    plist = None if request.POST.get('price_list') == "" else Fin_Price_List.objects.get(id = request.POST.get('price_list'))
    term = None if request.POST.get('pay_terms') == "" else Fin_Company_Payment_Terms.objects.get(id = request.POST.get('pay_terms'))
    pbill = Fin_Purchase_Bill(vendor = ven,
        customer = cust,
        pricelist = plist,
        ven_psupply = request.POST.get('ven_psupply'),
        cust_psupply = request.POST.get('cust_psupply'),
        bill_no = request.POST.get('bill_no'),
        ref_no = request.POST.get('ref_no'),
        porder_no = request.POST.get('pord_no'),
        bill_date = request.POST.get('bill_date'),
        due_date = request.POST.get('due_date'),
        pay_term = term,
        pay_type = request.POST.get('pay_type'),
        cheque_no = request.POST.get('cheque_id'),
        upi_no = request.POST.get('upi_id'),
        bank_no = request.POST.get('bnk_no'),
        subtotal = request.POST.get('sub_total'),
        igst = request.POST.get('igst'),
        cgst = request.POST.get('cgst'),
        sgst = request.POST.get('sgst'),
        taxamount = request.POST.get('tax_amount'),
        ship_charge = request.POST.get('shipcharge'),
        adjust = request.POST.get('adjustment'),
        grandtotal = request.POST.get('grand_total'),
        paid = request.POST.get('paid'),
        balance = request.POST.get('bal_due'),
        status = "Save",
        company = com,
        logindetails = com.Login_Id
    )

    pbill.save()
        
    item = tuple(request.POST.getlist("product[]"))
    qty =  tuple(request.POST.getlist("qty[]"))
    price =  tuple(request.POST.getlist("price[]"))
    if request.POST.getlist("intra_tax[]")[0] != '':
        tax = tuple(request.POST.getlist("intra_tax[]"))
    else:
        tax = tuple(request.POST.getlist("inter_tax[]"))
    discount =  tuple(request.POST.getlist("discount[]"))
    total =  tuple(request.POST.getlist("total[]"))

    if len(item)==len(qty)==len(price)==len(tax)==len(discount)==len(total):
        mapped=zip(item,qty,price,tax,discount,total)
        mapped=list(mapped)
        for ele in mapped:
            itm = Fin_Items.objects.get(id=ele[0])
            Fin_Purchase_Bill_Item.objects.create(item = itm,qty = ele[1],price = float(ele[2]),tax = ele[3],discount = float(ele[4]),total = float(ele[5]),pbill = pbill,company = com)
            itm.current_stock = int(itm.current_stock) + int(ele[1])
            itm.save()

    Fin_Purchase_Bill_Ref_No.objects.create(company = com, logindetails = data, ref_no = request.POST.get('ref_no'))
    Fin_Purchase_Bill_History.objects.create(company =com, logindetails = data, pbill = pbill, action='Created')

    # Save Bill details to Purchase Order

    purchaseOrder.converted_to_bill = pbill
    purchaseOrder.save()

    return redirect(Fin_purchaseOrder)
  else:
    return redirect(Fin_purchaseOrder)

# End

def StockAdjustment(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            
        elif data.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
            allmodules = Fin_Modules_List.objects.get(company_id = com,status = 'New')

        terms = Fin_Payment_Terms.objects.all()
        noti = Fin_CNotification.objects.filter(status = 'New',Company_id = com)
        n = len(noti)
        stock_adj= Stock_Adjustment.objects.filter(company=com)
        return render(request,'company/Fin_StockAdjustment.html',{'allmodules':allmodules,'com':com,'data':data,'terms':terms,'noti':noti,'n':n,'stock_adj':stock_adj})  

def AddStockAdjustment(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
   
        elif data.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
            allmodules = Fin_Modules_List.objects.get(company_id = com,status = 'New')

        noti = Fin_CNotification.objects.filter(status = 'New',Company_id = com)
        n = len(noti)
        items=Fin_Items.objects.filter(Company = com)
        accounts=Fin_Chart_Of_Account.objects.filter(Company=com)
        date=datetime.now()
        reason=Stock_Reason.objects.filter(company=com)

        latest_inv = Stock_Adjustment.objects.filter(company = com).order_by('-id').first()
        new_number = int(latest_inv.reference_no) + 1 if latest_inv else 1
        if Stock_Adjustment_RefNo.objects.filter(company = com).exists():
            deleted = Stock_Adjustment_RefNo.objects.get(company = com)
            if deleted:
                while int(deleted.reference_no) >= new_number:
                    new_number+=1

        return render(request,'company/Fin_AddStockAdjustment.html',{'allmodules':allmodules,'com':com,'n':n,'data':data,'items':items,'accounts':accounts,'date':date,'reason':reason,'ref_no':new_number})  
        


def Fin_StockAdjustmentView(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New') 

        elif data.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
            allmodules = Fin_Modules_List.objects.get(company_id = com,status = 'New')

        terms = Fin_Payment_Terms.objects.all()
        noti = Fin_CNotification.objects.filter(status = 'New',Company_id = com)
        n = len(noti)
        return render(request,'company/Fin_StockAdjustmentView.html',{'allmodules':allmodules,'com':com,'data':data,'terms':terms,'noti':noti,'n':n})
        

def getitemdata1(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)

        elif data.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        item_name=request.GET.get('id')
        items=Fin_Items.objects.filter(Company = com,name=item_name)
        stock=0
        for i in items:
            stock=i.current_stock
        return JsonResponse({'stock':stock})
        
def getitemdata2(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)

        elif data.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        item_name=request.GET.get('id')
        items=Fin_Items.objects.filter(Company = com,name=item_name)
        stock=0
        purchase_price=0
        value=0
        
        for i in items:
            stock=i.current_stock
            purchase_price=i.purchase_price
            value=stock*purchase_price
        print(value,'value')
        return JsonResponse({'value':value})
    
        


def create_stockadjustment(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if request.method == 'POST':
            
            if data.User_Type == "Company":
                com = Fin_Company_Details.objects.get(Login_Id = s_id)
            elif data.User_Type == 'Staff':
                com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

            mode_of_adj= request.POST['mode']
            ref_no=request.POST['refno']
            date=request.POST['date']
            account=request.POST['account']
            reason=request.POST['reason']
            description = request.POST['desc']
            if 'file' in request.FILES:
                attach_file = request.FILES['file']
            else:
                attach_file = None
                
            stock_adjustment=Stock_Adjustment.objects.create(
                company=com,
                login_details=data,
                mode_of_adjustment=mode_of_adj,
                reference_no=ref_no,
                adjusting_date=date,
                account=account,
                reason=reason,
                description=description,
                attach_file = attach_file,

            )
            stock_adjustment.save()

            if 'draft' in request.POST:
                stock_adjustment.status = "Draft"

            elif 'save' in request.POST:
                stock_adjustment.status = "Save"

            stock_adjustment.save()

            if mode_of_adj == 'Quantity':
                item_names = request.POST.getlist('item1')
                print('item_names asdsadas',item_names)
                qty_available = request.POST.getlist('qtyav[]')
                new_qty_on_hand = request.POST.getlist('newqty[]')
                print(new_qty_on_hand,"new_qty_on_hand is")
                qty_adjusted = request.POST.getlist('qtyadj[]')

                if len(item_names) == len(qty_available) == len(new_qty_on_hand) == len(qty_adjusted):
                    for i in range(len(item_names)):

                        item_instance = Fin_Items.objects.get(name=item_names[i],Company=com)
                        item_instance.current_stock += int(new_qty_on_hand[i])
                        item_instance.save()

                        items1 = Stock_Adjustment_Items.objects.create(
                            item=item_instance,
                            quantity_avail=qty_available[i],
                            quantity_inhand=new_qty_on_hand[i],
                            quantity_adj=qty_adjusted[i],
                            stock_adjustment=stock_adjustment,
                            company=com,
                            type='Quantity',
                            login_details=data,
                            
                        )
                        items1.save()
                        
                        stock_adj_history = Stock_Adjustment_History.objects.create(
                        company=com,
                        login_details=data,
                        item=item_instance,
                        date=date,
                        action='Created',
                        stock_adjustment=stock_adjustment
                    )
                        stock_adj_history.save()


            elif mode_of_adj == 'Value':
                items= request.POST.getlist('item2[]')
                current_value = request.POST.getlist('cuval[]')
                changed_value = request.POST.getlist('chval[]')
                value_adjusted = request.POST.getlist('adjval[]')

                if len(items) == len(current_value) == len(changed_value) == len(value_adjusted):
                    for j in range(len(items)):

                        item_inst = Fin_Items.objects.get(name=items[j])

                        item_list= Stock_Adjustment_Items.objects.create(
                            item=item_inst,
                            current_val = current_value[j],
                            changed_val = changed_value[j],
                            adjusted_val = value_adjusted[j],
                            company=com,
                            login_details=data,
                            stock_adjustment=stock_adjustment,
                            type='Value'
                        )
                        item_list.save()

                        stock_adj_history = Stock_Adjustment_History.objects.create(
                            company=com,
                            login_details=data,
                            item=item_inst,
                            date=date,
                            action = 'Created',
                            stock_adjustment=stock_adjustment
                    )
                    stock_adj_history.save()

            return redirect('StockAdjustment')
            

            
def StockAdjustmentOverview(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)

        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')

        elif data.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
            allmodules = Fin_Modules_List.objects.get(company_id = com,status = 'New')

        terms = Fin_Payment_Terms.objects.all()
        noti = Fin_CNotification.objects.filter(status = 'New',Company_id = com)
        n = len(noti)
        stocks=Stock_Adjustment.objects.get(id=id,company=com)
        st_items=Stock_Adjustment_Items.objects.filter(stock_adjustment =stocks,company = com)
        comment=Stock_Adjustment_Comment.objects.filter(stock_adjustment=id,company=com)
        return render(request,'company/Fin_StockAdjustmentOverview.html',{'allmodules':allmodules,'com':com,'data':data,'terms':terms,'noti':noti,'n':n,'stocks':stocks,'comment':comment,'st_items':st_items})


def del_stockadj(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)

        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)

        elif data.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        stocks=Stock_Adjustment.objects.get(id=id,company=com)
        stock=Stock_Adjustment_Items.objects.filter(stock_adjustment=id,company=com)
        comment=Stock_Adjustment_Comment.objects.filter(stock_adjustment=id,company=com)
        stocks.delete()
        stock.delete()
        comment.delete()
        return redirect('StockAdjustment')  

        
def stockadj_comment(request,id):
     if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)

        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)

        elif data.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        if request.method == 'POST':
            stock = Stock_Adjustment.objects.get(id=id,company=com)
            comment = request.POST['comment']
            add_comment=Stock_Adjustment_Comment.objects.create(
                company=com,
                login_details=data,
                stock_adjustment=stock,
                comment=comment
            )
            add_comment.save()
            
            return redirect('StockAdjustmentOverview',id)
        return render('StockAdjustmentOverview',id)
        

def del_stockcmnt(request,id):
     if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)

        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)

        elif data.User_Type == 'Staff':
             com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        comment=Stock_Adjustment_Comment.objects.get(id=id,company=com)
        comment.delete()
        return redirect('StockAdjustmentOverview',id)
     return render('StockAdjustmentOverview',id)


def add_reason(request):
     if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)

        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id 

        reason = request.POST['reason']
        
        if not Stock_Reason.objects.filter(company = com, reason__iexact = reason).exists():
            Stock_Reason.objects.create(company = com, reason = reason)

            reasonlist = []
            reasons = Stock_Reason.objects.filter(company = com)

            for i in reasons:
             keyPairReason={
                 'name':i.reason,
                 'id':i.id
             }
             reasonlist.append(keyPairReason)
            
            return JsonResponse({'status':True,'reasons':reasonlist},safe=False)
        else:
            return JsonResponse({'status':False, 'message':f'{reason} already exists, try another.!'})


def convert_stockadj(request,id):
     if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        elif data.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        if request.method == 'POST':   
            stockadj = Stock_Adjustment.objects.get(id=id,company=com)
            stockadj.status="Save"
            stockadj.save()
        return redirect('StockAdjustmentOverview',id)
     return redirect('StockAdjustmentOverview',id)


def Stk_adjHistory(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
        elif data.User_Type == 'Staff':
             com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
             allmodules = Fin_Modules_List.objects.get(company_id = com,status = 'New')

        stockadj = Stock_Adjustment.objects.get(id=id,company=com)
        stockadj_history=Stock_Adjustment_History.objects.filter(stock_adjustment=stockadj,company=com)
        return render(request,'company/Fin_StockAdjustmentHistory.html',{'history':stockadj_history,'allmodules':allmodules})
    return redirect('StockAdjustmentOverview',id)


def edit_stockadj(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)

        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            
            
        elif data.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
            allmodules = Fin_Modules_List.objects.get(company_id = com,status = 'New')

        terms = Fin_Payment_Terms.objects.all()
        noti = Fin_CNotification.objects.filter(status = 'New',Company_id = com)
        n = len(noti)
        stocks=Stock_Adjustment.objects.get(id=id,company=com)
        st_items=Stock_Adjustment_Items.objects.filter(stock_adjustment =stocks,company = com)
        cnt_item=Stock_Adjustment_Items.objects.filter(stock_adjustment =stocks,company = com).count()
        items=Fin_Items.objects.filter(Company = com)
        reason=Stock_Reason.objects.filter(company=com)
        return render(request,'company/Fin_EditStockAdjustment.html',{'reason':reason,'cnt_item':cnt_item,'allmodules':allmodules,'com':com,'data':data,'terms':terms,'noti':noti,'n':n,'stocks':stocks,'st_items':st_items,'items':items})
        

def updatedStockAdj(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)

        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)

        elif data.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        if request.method=='POST':
            stck_adj=Stock_Adjustment.objects.get(id=id)
            stck_adj.mode_of_adjustment= request.POST['mode']
            stck_adj.reference_no=request.POST['refno']
            stck_adj.adjusting_date=request.POST['date']
            stck_adj.account=request.POST['account']
            stck_adj.reason=request.POST['reason']
            stck_adj.description = request.POST['desc']
            if 'file' in request.FILES:
                stck_adj.attach_file = request.FILES['file']
            else:
                stck_adj.attach_file = None
            stck_adj.company=com
            stck_adj.login_details=data
            stck_adj.save()

            if 'draft' in request.POST:
                stck_adj.status = "Draft"

            elif 'save' in request.POST:
                stck_adj.status = "Save"

            stck_adj.save()

            stckItem_adj=Stock_Adjustment_Items.objects.filter(stock_adjustment=stck_adj.id)
            stckItem_adj.delete()

            if stck_adj.mode_of_adjustment == 'Quantity':
                item_names = request.POST.getlist('item1')
                qty_available = request.POST.getlist('qtyav[]')
                new_qty_on_hand = request.POST.getlist('newqty[]')
                qty_adjusted = request.POST.getlist('qtyadj[]')

                if len(item_names) == len(qty_available) == len(new_qty_on_hand) == len(qty_adjusted):
                    for i in range(len(item_names)):

                        item_instance = Fin_Items.objects.get(name=item_names[i],Company=com)
                        item_instance.current_stock += float(new_qty_on_hand[i])
                        item_instance.save()

                        items1 = Stock_Adjustment_Items.objects.create(
                            item=item_instance,
                            quantity_avail=qty_available[i],
                            quantity_inhand=new_qty_on_hand[i],
                            quantity_adj=qty_adjusted[i],
                            stock_adjustment=stck_adj,
                            company=com,
                            type='Quantity',
                            login_details=data,
                            
                        )
                        items1.save()
                        
                        stock_adj_history = Stock_Adjustment_History.objects.create(
                        company=com,
                        login_details=data,
                        item=item_instance,
                        date=stck_adj.adjusting_date,
                        action='Edited',
                        stock_adjustment=stck_adj
                    )
                        stock_adj_history.save()


            elif stck_adj.mode_of_adjustment == 'Value':
                items= request.POST.getlist('item2[]')
                current_value = request.POST.getlist('cuval[]')
                changed_value = request.POST.getlist('chval[]')
                value_adjusted = request.POST.getlist('adjval[]')

                if len(items) == len(current_value) == len(changed_value) == len(value_adjusted):
                    for j in range(len(items)):

                        item_inst = Fin_Items.objects.get(name=items[j])

                        item_list= Stock_Adjustment_Items.objects.create(
                            item=item_inst,
                            current_val = current_value[j],
                            changed_val = changed_value[j],
                            adjusted_val = value_adjusted[j],
                            company=com,
                            login_details=data,
                            stock_adjustment=stck_adj,
                            type='Value'
                        )
                        item_list.save()

                        stock_adj_history = Stock_Adjustment_History.objects.create(
                            company=com,
                            login_details=data,
                            item=item_inst,
                            date=stck_adj.adjusting_date,
                            action='Edited',
                            stock_adjustment=stck_adj
                    )
                    stock_adj_history.save()
            return redirect('StockAdjustmentOverview',id)
        return redirect('StockAdjustmentOverview',id)
        
            
def deleteitem(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)

        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)

        elif data.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        stckItem_adj=Stock_Adjustment_Items.objects.get(id=id,company=com)
        stckItem_adj.delete()
        return JsonResponse({'message': 'Item deleted successfully'}) 
        

def filterbySave(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)

        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
        
        elif data.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
            allmodules = Fin_Modules_List.objects.get(company_id = com,status = 'New')

        terms = Fin_Payment_Terms.objects.all()
        noti = Fin_CNotification.objects.filter(status = 'New',Company_id = com)
        n = len(noti)
        stock_adj= Stock_Adjustment.objects.filter(company=com,status="Save")
        return render(request,'company/Fin_StockAdjustment.html',{'allmodules':allmodules,'com':com,'data':data,'terms':terms,'noti':noti,'n':n,'stock_adj':stock_adj})
        

def filterbyDraft(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')

        elif data.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
            allmodules = Fin_Modules_List.objects.get(company_id = com,status = 'New')

        noti = Fin_CNotification.objects.filter(status = 'New',Company_id = com)
        n = len(noti)
        stock_adj= Stock_Adjustment.objects.filter(company=com,status="Draft")
        return render(request,'company/Fin_StockAdjustment.html',{'allmodules':allmodules,'com':com,'data':data,'noti':noti,'n':n,'stock_adj':stock_adj})
        

def stock_attachFile(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)

        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)

        elif data.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        stock_adj= Stock_Adjustment.objects.get(company=com,id=id)
        if request.method == 'POST':
            if len(request.FILES) != 0:
            
                if stock_adj.attach_file != "":
                    os.remove(stock_adj.attach_file.path)
                stock_adj.attach_file=request.FILES['file']
            stock_adj.save()
        return redirect('StockAdjustmentOverview',id)
        
           
def stockadjToEmail(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)

        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        elif data.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        stock_adj= Stock_Adjustment.objects.get(company=com,id=id)
        stock_adjItems= Stock_Adjustment_Items.objects.filter(stock_adjustment=stock_adj,company=com)

        try:
            if request.method == 'POST':
                    emails_string = request.POST['email_ids']
                    emails_list = [email.strip() for email in emails_string.split(',')]
                    email_message = request.POST['email_message']
                    context = {'com': com, 'stocks': stock_adj, 'email_message': email_message,'st_items':stock_adjItems}
                    print('context working')
                    template_path = 'company/Fin_StockAdjustment_Pdf.html'
                    print('tpath working')
                    template = get_template(template_path)
                    print('template working')
                    html = template.render(context)
                    print('html working')
                    result = BytesIO()
                    print('bytes working')
                    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)  # Change encoding to 'utf-8'
                    print('pisa working')
                    if pdf.err:
                        raise Exception(f"PDF generation error: {pdf.err}")
                    result.seek(0)  # Move the buffer's position to the start for reading
                    filename = f'Stock_AdjusmentDetails_{stock_adj.reference_no}.pdf'
                    subject = f"Stock_AdjusmentDetails_{stock_adj.reference_no}"
                    email = EmailMessage(subject, f"Hi,\nPlease find the attached Stock Adjustment Details for Reference No: {stock_adj.reference_no}. \n{email_message}\n\n--\nRegards,\n{com.Company_name}\n{com.Address}\n{com.State} - {com.Country}\n{com.Contact}", from_email=settings.EMAIL_HOST_USER, to=emails_list)
                    email.attach(filename, result.read(), "application/pdf")  # Use result.read() directly
                    email.send(fail_silently=False)
                    messages.success(request, 'Stock Adjusment details has been shared via email successfully..!')
                    return redirect('StockAdjustmentOverview', id=id)
            return redirect('StockAdjustmentOverview', id=id)
        except Exception as e:
                print(e)
                messages.error(request, f'{e}')
                return redirect(StockAdjustmentOverview, id)


# myyyy
def deliverylist(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            cmp = com
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            cmp = com.company_id
        
        allmodules = Fin_Modules_List.objects.get(company_id = cmp,status = 'New')
        deli = Fin_Delivery_Challan.objects.filter(Company = cmp)
        return render(request,'company/Fin_Delivery_Challan.html',{'allmodules':allmodules,'com':com, 'cmp':cmp,'data':data,'del':deli})
    else:
       return redirect('/')
     
     

    


def Fin_getCustomerschallan(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        options = {}
        option_objects = Fin_Customers.objects.filter(Company = com, status = 'Active')
        for option in option_objects:
            options[option.id] = [option.id , option.title, option.first_name, option.last_name]

        return JsonResponse(options)
    else:
        return redirect('/')
    

def Fin_createchallanCustomer(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        fName = request.POST['first_name']
        lName = request.POST['last_name']
        gstIn = request.POST['gstin']
        pan = request.POST['pan_no']
        email = request.POST['email']
        phn = request.POST['mobile']

        if Fin_Customers.objects.filter(Company = com, first_name__iexact = fName, last_name__iexact = lName).exists():
            res = f"Customer `{fName} {lName}` already exists, try another!"
            return JsonResponse({'status': False, 'message':res})
        elif gstIn != "" and Fin_Customers.objects.filter(Company = com, gstin__iexact = gstIn).exists():
            res = f"GSTIN `{gstIn}` already exists, try another!"
            return JsonResponse({'status': False, 'message':res})
        elif Fin_Customers.objects.filter(Company = com, pan_no__iexact = pan).exists():
            res = f"PAN No `{pan}` already exists, try another!"
            return JsonResponse({'status': False, 'message':res})
        elif Fin_Customers.objects.filter(Company = com, mobile__iexact = phn).exists():
            res = f"Phone Number `{phn}` already exists, try another!"
            return JsonResponse({'status': False, 'message':res})
        elif Fin_Customers.objects.filter(Company = com, email__iexact = email).exists():
            res = f"Email `{email}` already exists, try another!"
            return JsonResponse({'status': False, 'message':res})

        cust = Fin_Customers(
            Company = com,
            LoginDetails = data,
            title = request.POST['title'],
            first_name = fName,
            last_name = lName,
            company = request.POST['company_name'],
            location = request.POST['location'],
            place_of_supply = request.POST['place_of_supply'],
            gst_type = request.POST['gst_type'],
            gstin = None if request.POST['gst_type'] == "Unregistered Business" or request.POST['gst_type'] == 'Overseas' or request.POST['gst_type'] == 'Consumer' else gstIn,
            pan_no = pan,
            email = email,
            mobile = phn,
            website = request.POST['website'],
            price_list = None if request.POST['price_list'] ==  "" else Fin_Price_List.objects.get(id = request.POST['price_list']),
            payment_terms = None if request.POST['payment_terms'] == "" else Fin_Company_Payment_Terms.objects.get(id = request.POST['payment_terms']),
            opening_balance = 0 if request.POST['open_balance'] == "" else float(request.POST['open_balance']),
            open_balance_type = request.POST['balance_type'],
            current_balance = 0 if request.POST['open_balance'] == "" else float(request.POST['open_balance']),
            credit_limit = 0 if request.POST['credit_limit'] == "" else float(request.POST['credit_limit']),
            billing_street = request.POST['street'],
            billing_city = request.POST['city'],
            billing_state = request.POST['state'],
            billing_pincode = request.POST['pincode'],
            billing_country = request.POST['country'],
            ship_street = request.POST['shipstreet'],
            ship_city = request.POST['shipcity'],
            ship_state = request.POST['shipstate'],
            ship_pincode = request.POST['shippincode'],
            ship_country = request.POST['shipcountry'],
            status = 'Active'
        )
        cust.save()

        #save transaction

        Fin_Customers_History.objects.create(
            Company = com,
            LoginDetails = data,
            customer = cust,
            action = 'Created'
        )

        return JsonResponse({'status': True})
    
    else:
        return redirect('/')
 

def customerdata(request):
    sid = request.session['s_id']
    login = Fin_Login_Details.objects.get(id=sid)
    
    if login.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        customer_id = request.GET.get('id')
        print(customer_id)
        cust = Fin_Customers.objects.get(id=customer_id,Company_id=com.id)
        print('h')
        data7 = {'email': cust.email,'billing_street':cust.billing_street,'billing_city':cust.billing_city,'billing_state':cust.billing_state,'gst_type':cust.gst_type,'gstin':cust.gstin,'place_of_supply':cust.place_of_supply}
        return JsonResponse(data7)

      
        
    elif login.User_Type == 'Staff' :
        staf = Fin_Staff_Details.objects.get(Login_Id = sid)
        customer_id = request.GET.get('id')
        cust = Fin_Customers.objects.get(id=customer_id,Company_id=staf.company_id_id)
        data7 = {'email': cust.email,'billing_street':cust.billing_street,'billing_city':cust.billing_city,'billing_state':cust.billing_state,'gst_type':cust.gst_type,'gstin':cust.gstin,'place_of_supply':cust.place_of_supply,}
        return JsonResponse(data7)





def challan_overview(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)

        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            cmp = com
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            cmp = com.company_id
        
        allmodules = Fin_Modules_List.objects.get(company_id = cmp,status = 'New')
        Estimate = Fin_Delivery_Challan.objects.get(id = id)
        cmt = Fin_Delivery_Challan_Comments.objects.filter(delivery_challan = Estimate)
        hist = Fin_Delivery_Challan_History.objects.filter(delivery_challan = Estimate).last()
        EstItems = Fin_Delivery_Challan_Items.objects.filter(delivery_challan = Estimate)
        histpry = Fin_Delivery_Challan_History.objects.filter(delivery_challan = Estimate)
        try:
            created = Fin_Delivery_Challan_History.objects.get(delivery_challan = Estimate, action = 'Created')
        except:
            created = None
#  'comments':cmt, 
        return render(request,'company/Fin_Delivery_Challan_View.html',{'allmodules':allmodules,'com':com,'cmp':cmp, 'data':data, 'estimate':Estimate,'estItems':EstItems, 'history':hist,'created':created,'comments':cmt,'histpry2':histpry})
    else:
       return redirect('/')



   
def Fin_editchallanto(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            cmp = com
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            cmp = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = cmp,status = 'New')
        est = Fin_Delivery_Challan.objects.get(id = id)
        estItms = Fin_Delivery_Challan_Items.objects.filter(delivery_challan = est)
        cust = Fin_Customers.objects.filter(Company = cmp, status = 'Active')
        itms = Fin_Items.objects.filter(Company = cmp, status = 'Active')
       
        context = {
            'allmodules':allmodules, 'com':com, 'cmp':cmp, 'data':data,'estimate':est, 'estItems':estItms, 'customers':cust, 'items':itms
           
        }
        return render(request,'company/Fin_Delivery_Challan_Edit.html',context)
    else:
       return redirect('/')


def Fin_deleteChallan(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        est = Fin_Delivery_Challan.objects.get( id = id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        Fin_Delivery_Challan_Items.objects.filter(delivery_challan = est).delete()

        # Storing ref number to deleted table
        # if entry exists and lesser than the current, update and save => Only one entry per company
        if Fin_Delivery_Challan_Reference.objects.filter(Company = com).exists():
            deleted = Fin_Delivery_Challan_Reference.objects.get(Company = com)
            if int(est.reference_no) > int(deleted.reference_number):
                deleted.reference_no = est.reference_no
                deleted.save()
        else:
            Fin_Delivery_Challan_Reference.objects.create(Company = com, reference_no = est.reference_no)
        
        est.delete()
        return redirect(deliverylist)

def Fin_addchallanComment(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        est = Fin_Delivery_Challan.objects.get(id = id)
        if request.method == "POST":
            cmt = request.POST['comment'].strip()

            Fin_Delivery_Challan_Comments.objects.create(Company = com, delivery_challan = est, comments = cmt)
            return redirect(challan_overview, id)
        return redirect(challan_overview, id)
    return redirect('/')


def Fin_deletechallanComment(request,id):
    if 's_id' in request.session:
        cmt = Fin_Delivery_Challan_Comments.objects.get(id = id)
        estId = cmt.delivery_challan.id
        cmt.delete()
        return redirect(challan_overview, estId)


def Fin_attachchallanFile(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        est = Fin_Delivery_Challan.objects.get(id = id)

        if request.method == 'POST' and len(request.FILES) != 0:
            est.document = request.FILES.get('file')
            est.save()

        return redirect(challan_overview, id)
    else:
        return redirect('/')
    
def Fin_convertchallan(request,id):
    if 's_id' in request.session:

        est = Fin_Delivery_Challan.objects.get(id = id)
        est.status = 'Saved'
        est.save()
        return redirect(challan_overview, id)

def Fin_convertchallanToInvoice(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            cmp = com
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            cmp = com.company_id

        est = Fin_Delivery_Challan.objects.get(id = id)
        estItms = Fin_Delivery_Challan_Items.objects.filter(delivery_challan = est)
        cust = Fin_Customers.objects.filter(Company = cmp, status = 'Active')
        itms = Fin_Items.objects.filter(Company = cmp, status = 'Active')
        trms = Fin_Company_Payment_Terms.objects.filter(Company = cmp)
        bnk = Fin_Banking.objects.filter(company = cmp)
        lst = Fin_Price_List.objects.filter(Company = cmp, status = 'Active')
        units = Fin_Units.objects.filter(Company = cmp)
        acc = Fin_Chart_Of_Account.objects.filter(Q(account_type='Expense') | Q(account_type='Other Expense') | Q(account_type='Cost Of Goods Sold'), Company=cmp).order_by('account_name')

        # Fetching last invoice and assigning upcoming ref no as current + 1
        # Also check for if any bill is deleted and ref no is continuos w r t the deleted invoice
        latest_inv = Fin_Invoice.objects.filter(Company = cmp).order_by('-id').first()

        new_number = int(latest_inv.reference_no) + 1 if latest_inv else 1

        if Fin_Invoice_Reference.objects.filter(Company = cmp).exists():
            deleted = Fin_Invoice_Reference.objects.get(Company = cmp)
            
            if deleted:
                while int(deleted.reference_no) >= new_number:
                    new_number+=1

        # Finding next invoice number w r t last invoic number if exists.
        nxtInv = ""
        lastInv = Fin_Invoice.objects.filter(Company = cmp).last()
        if lastInv:
            inv_no = str(lastInv.invoice_no)
            numbers = []
            stri = []
            for word in inv_no:
                if word.isdigit():
                    numbers.append(word)
                else:
                    stri.append(word)
            
            num=''
            for i in numbers:
                num +=i
            
            st = ''
            for j in stri:
                st = st+j

            inv_num = int(num)+1

            if num[0] == '0':
                if inv_num <10:
                    nxtInv = st+'0'+ str(inv_num)
                else:
                    nxtInv = st+ str(inv_num)
            else:
                nxtInv = st+ str(inv_num)

        context = {
            'allmodules':allmodules, 'com':com, 'cmp':cmp, 'data':data,'estimate':est, 'estItems':estItms, 'customers':cust, 'items':itms, 'pTerms':trms,'list':lst,
            'banks':bnk,'units':units, 'accounts':acc,'ref_no':new_number,'invNo':nxtInv
        }
        return render(request,'company/Fin_Convert_Delivery_Challan_toInvoice.html',context)
    else:
       return redirect('/')


def Fin_estimatechallanInvoice(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        est = Fin_Delivery_Challan.objects.get(id = id)
        if request.method == 'POST':
            invNum = request.POST['invoice_no']
            if Fin_Invoice.objects.filter(Company = com, invoice_no__iexact = invNum).exists():
                res = f'<script>alert("Invoice Number `{invNum}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)

            inv = Fin_Invoice(
                Company = com,
                LoginDetails = com.Login_Id,
                Customer = Fin_Customers.objects.get(id = request.POST['customer']),
                customer_email = request.POST['customerEmail'],
                billing_address = request.POST['bill_address'],
                gst_type = request.POST['gst_type'],
                gstin = request.POST['gstin'],
                place_of_supply = request.POST['place_of_supply'],
                reference_no = request.POST['reference_number'],
                invoice_no = invNum,
                payment_terms = Fin_Company_Payment_Terms.objects.get(id = request.POST['payment_term']),
                invoice_date = request.POST['invoice_date'],
                duedate = datetime.strptime(request.POST['due_date'], '%d-%m-%Y').date(),
                salesOrder_no = request.POST['order_number'],
                exp_ship_date = datetime.strptime(request.POST['due_date'], '%d-%m-%Y').date(),
                price_list_applied = True if 'priceList' in request.POST else False,
                payment_method = None if request.POST['payment_method'] == "" else request.POST['payment_method'],
                cheque_no = None if request.POST['cheque_id'] == "" else request.POST['cheque_id'],
                upi_no = None if request.POST['upi_id'] == "" else request.POST['upi_id'],
                bank_acc_no = None if request.POST['bnk_id'] == "" else request.POST['bnk_id'],
                subtotal = 0.0 if request.POST['subtotal'] == "" else float(request.POST['subtotal']),
                igst = 0.0 if request.POST['igst'] == "" else float(request.POST['igst']),
                cgst = 0.0 if request.POST['cgst'] == "" else float(request.POST['cgst']),
                sgst = 0.0 if request.POST['sgst'] == "" else float(request.POST['sgst']),
                tax_amount = 0.0 if request.POST['taxamount'] == "" else float(request.POST['taxamount']),
                adjustment = 0.0 if request.POST['adj'] == "" else float(request.POST['adj']),
                shipping_charge = 0.0 if request.POST['ship'] == "" else float(request.POST['ship']),
                grandtotal = 0.0 if request.POST['grandtotal'] == "" else float(request.POST['grandtotal']),
                paid_off = 0.0 if request.POST['advance'] == "" else float(request.POST['advance']),
                balance = request.POST['grandtotal'] if request.POST['balance'] == "" else float(request.POST['balance']),
                note = request.POST['note'],
                status = "Saved" 
            )

            inv.save()

            if len(request.FILES) != 0:
                inv.file=request.FILES.get('file')
            inv.save()

            # Save invoice items.

            itemId = request.POST.getlist("item_id[]")
            itemName = request.POST.getlist("item_name[]")
            hsn  = request.POST.getlist("hsn[]")
            qty = request.POST.getlist("qty[]")
            price = request.POST.getlist("priceListPrice[]") if 'priceList' in request.POST else request.POST.getlist("price[]")
            tax = request.POST.getlist("taxGST[]") if request.POST['place_of_supply'] == com.State else request.POST.getlist("taxIGST[]")
            discount = request.POST.getlist("discount[]")
            total = request.POST.getlist("total[]")

            if len(itemId)==len(itemName)==len(hsn)==len(qty)==len(price)==len(tax)==len(discount)==len(total) and itemId and itemName and hsn and qty and price and tax and discount and total:
                mapped = zip(itemId,itemName,hsn,qty,price,tax,discount,total)
                mapped = list(mapped)
                for ele in mapped:
                    itm = Fin_Items.objects.get(id = int(ele[0]))
                    Fin_Invoice_Items.objects.create(Invoice = inv, Item = itm, hsn = ele[2], quantity = int(ele[3]), price = float(ele[4]), tax = ele[5], discount = float(ele[6]), total = float(ele[7]))
                    itm.current_stock -= int(ele[3])
                    itm.save()
            
            # Save transaction
                    
            Fin_Invoice_History.objects.create(
                Company = com,
                LoginDetails = data,
                Invoice = inv,
                action = 'Created'
            )

            # Save invoice and balance details to Estimate

            est.converted_to_invoice = inv
            est.balance = float(inv.balance)
            est.save()

            return redirect(deliverylist)
        else:
            return redirect(deliverylist, id)
    else:
       return redirect('/')


def Fin_convertchallanToRecurringInvoice(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            cmp = com
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            cmp = com.company_id

        est = Fin_Delivery_Challan.objects.get(id = id)
        estItms = Fin_Delivery_Challan_Items.objects.filter(delivery_challan = est)
        cust = Fin_Customers.objects.filter(Company = cmp, status = 'Active')
        itms = Fin_Items.objects.filter(Company = cmp, status = 'Active')
        trms = Fin_Company_Payment_Terms.objects.filter(Company = cmp)
        bnk = Fin_Banking.objects.filter(company = cmp)
        lst = Fin_Price_List.objects.filter(Company = cmp, status = 'Active')
        units = Fin_Units.objects.filter(Company = cmp)
        acc = Fin_Chart_Of_Account.objects.filter(Q(account_type='Expense') | Q(account_type='Other Expense') | Q(account_type='Cost Of Goods Sold'), Company=cmp).order_by('account_name')
        repeat = Fin_CompanyRepeatEvery.objects.filter(company = cmp)
        priceList = Fin_Price_List.objects.filter(Company = cmp, type = 'Sales', status = 'Active')

        # Fetching last invoice and assigning upcoming ref no as current + 1
        # Also check for if any bill is deleted and ref no is continuos w r t the deleted invoice
        latest_inv = Fin_Recurring_Invoice.objects.filter(Company = cmp).order_by('-id').first()

        new_number = int(latest_inv.reference_no) + 1 if latest_inv else 1

        if Fin_Recurring_Invoice_Reference.objects.filter(Company = cmp).exists():
            deleted = Fin_Recurring_Invoice_Reference.objects.get(Company = cmp)
            
            if deleted:
                while int(deleted.reference_no) >= new_number:
                    new_number+=1

        # Finding next rec_invoice number w r t last rec_invoice number if exists.
        nxtInv = ""
        lastInv = Fin_Recurring_Invoice.objects.filter(Company = cmp).last()
        if lastInv:
            inv_no = str(lastInv.rec_invoice_no)
            numbers = []
            stri = []
            for word in inv_no:
                if word.isdigit():
                    numbers.append(word)
                else:
                    stri.append(word)
            
            num=''
            for i in numbers:
                num +=i
            
            st = ''
            for j in stri:
                st = st+j

            inv_num = int(num)+1

            if num[0] == '0':
                if inv_num <10:
                    nxtInv = st+'0'+ str(inv_num)
                else:
                    nxtInv = st+ str(inv_num)
            else:
                nxtInv = st+ str(inv_num)
        else:
            nxtInv = 'RI01'

        context = {
            'allmodules':allmodules, 'com':com, 'cmp':cmp, 'data':data,'estimate':est, 'estItems':estItms, 'customers':cust, 'items':itms, 'pTerms':trms,'list':lst,
            'banks':bnk,'units':units, 'accounts':acc,'ref_no':new_number,'invNo':nxtInv, 'priceListItems':priceList, 'repeat':repeat,
        }
        return render(request,'company/Fin_Convert_Delivery_Challan_toRecInvoice.html',context)
    else:
       return redirect('/')   
    

def Fin_challanConvertRecInvoice(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        est = Fin_Delivery_Challan.objects.get(id = id)

        if request.method == 'POST':
            invNum = request.POST['rec_invoice_no']
            if Fin_Recurring_Invoice.objects.filter(Company = com, rec_invoice_no__iexact = invNum).exists():
                res = f'<script>alert("Rec. Invoice Number `{invNum}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)

            inv = Fin_Recurring_Invoice(
                Company = com,
                LoginDetails = com.Login_Id,
                Customer = Fin_Customers.objects.get(id = request.POST['customerId']),
                customer_email = request.POST['customerEmail'],
                billing_address = request.POST['bill_address'],
                gst_type = request.POST['gst_type'],
                gstin = request.POST['gstin'],
                place_of_supply = request.POST['place_of_supply'],
                profile_name = request.POST['profile_name'],
                entry_type = None if request.POST['entry_type'] == "" else request.POST['entry_type'],
                reference_no = request.POST['reference_number'],
                rec_invoice_no = invNum,
                payment_terms = Fin_Company_Payment_Terms.objects.get(id = request.POST['payment_term']),
                start_date = request.POST['start_date'],
                end_date = datetime.strptime(request.POST['end_date'], '%d-%m-%Y').date(),
                salesOrder_no = request.POST['order_number'],
                price_list_applied = True if 'priceList' in request.POST else False,
                price_list = None if request.POST['price_list_id'] == "" else Fin_Price_List.objects.get(id = request.POST['price_list_id']),
                repeat_every = Fin_CompanyRepeatEvery.objects.get(id = request.POST['repeat_every']),
                payment_method = None if request.POST['payment_method'] == "" else request.POST['payment_method'],
                cheque_no = None if request.POST['cheque_id'] == "" else request.POST['cheque_id'],
                upi_no = None if request.POST['upi_id'] == "" else request.POST['upi_id'],
                bank_acc_no = None if request.POST['bnk_id'] == "" else request.POST['bnk_id'],
                subtotal = 0.0 if request.POST['subtotal'] == "" else float(request.POST['subtotal']),
                igst = 0.0 if request.POST['igst'] == "" else float(request.POST['igst']),
                cgst = 0.0 if request.POST['cgst'] == "" else float(request.POST['cgst']),
                sgst = 0.0 if request.POST['sgst'] == "" else float(request.POST['sgst']),
                tax_amount = 0.0 if request.POST['taxamount'] == "" else float(request.POST['taxamount']),
                adjustment = 0.0 if request.POST['adj'] == "" else float(request.POST['adj']),
                shipping_charge = 0.0 if request.POST['ship'] == "" else float(request.POST['ship']),
                grandtotal = 0.0 if request.POST['grandtotal'] == "" else float(request.POST['grandtotal']),
                paid_off = 0.0 if request.POST['advance'] == "" else float(request.POST['advance']),
                balance = request.POST['grandtotal'] if request.POST['balance'] == "" else float(request.POST['balance']),
                note = request.POST['note']
            )

            inv.save()

            if len(request.FILES) != 0:
                inv.file=request.FILES.get('file')
            inv.save()

            if 'Draft' in request.POST:
                inv.status = "Draft"
            elif "Save" in request.POST:
                inv.status = "Saved" 
            inv.save()

            # Save rec_invoice items.

            itemId = request.POST.getlist("item_id[]")
            itemName = request.POST.getlist("item_name[]")
            hsn  = request.POST.getlist("hsn[]")
            qty = request.POST.getlist("qty[]")
            price = request.POST.getlist("priceListPrice[]") if 'priceList' in request.POST else request.POST.getlist("price[]")
            tax = request.POST.getlist("taxGST[]") if request.POST['place_of_supply'] == com.State else request.POST.getlist("taxIGST[]")
            discount = request.POST.getlist("discount[]")
            total = request.POST.getlist("total[]")

            if len(itemId)==len(itemName)==len(hsn)==len(qty)==len(price)==len(tax)==len(discount)==len(total) and itemId and itemName and hsn and qty and price and tax and discount and total:
                mapped = zip(itemId,itemName,hsn,qty,price,tax,discount,total)
                mapped = list(mapped)
                for ele in mapped:
                    itm = Fin_Items.objects.get(id = int(ele[0]))
                    Fin_Recurring_Invoice_Items.objects.create(RecInvoice = inv, Item = itm, hsn = ele[2], quantity = int(ele[3]), price = float(ele[4]), tax = ele[5], discount = float(ele[6]), total = float(ele[7]))
                    itm.current_stock -= int(ele[3])
                    itm.save()
            
            # Save transaction
                    
            Fin_Recurring_Invoice_History.objects.create(
                Company = com,
                LoginDetails = data,
                RecInvoice = inv,
                action = 'Created'
            )

            # Save sales order details to Estimate and update Estimate Balance

            est.converted_to_recurring_invoice = inv
            est.balance = float(inv.balance)
            est.save()

            return redirect(deliverylist)
        else:
            return redirect(Fin_convertchallanToRecurringInvoice, id)
    else:
       return redirect('/')
#End



def Fin_sharechallanToEmail(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        est = Fin_Delivery_Challan.objects.get(id = id)
        itms = Fin_Delivery_Challan_Items.objects.filter(delivery_challan = est)
        try:
            if request.method == 'POST':
                emails_string = request.POST['email_ids']

                # Split the string by commas and remove any leading or trailing whitespace
                emails_list = [email.strip() for email in emails_string.split(',')]
                email_message = request.POST['email_message']
                print(emails_list)
            
                context = {'estimate':est, 'estItems':itms,'cmp':com}
                template_path = 'company/Fin_Delivery_Challan_Pdf.html'
                template = get_template(template_path)

                html  = template.render(context)
                result = BytesIO()
                pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
                pdf = result.getvalue()
                filename = f'Challan{est.challan_no}'
                subject = f"Delivery_Challan{est.challan_no}"
                email = EmailMessage(subject, f"Hi,\nPlease find the attached delivery challan for - #-{est.challan_no}. \n{email_message}\n\n--\nRegards,\n{com.Company_name}\n{com.Address}\n{com.State} - {com.Country}\n{com.Contact}", from_email=settings.EMAIL_HOST_USER, to=emails_list)
                email.attach(filename, pdf, "application/pdf")
                email.send(fail_silently=False)

                messages.success(request, 'Challan details has been shared via email successfully..!')
                return redirect(challan_overview,id)
        except Exception as e:
            print(e)
            messages.error(request, f'{e}')
            return redirect(challan_overview, id)


def Fin_checkchallanNumber(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        EstNo = request.GET['EstNum']

        nxtEstNo = ""
        lastEstmate = Fin_Delivery_Challan.objects.filter(Company = com).last()
        # lastEstmate = Fin_Delivery_Challan.objects.filter(Company=com).last()
        if lastEstmate:
                eway_no = str(lastEstmate.challan_no)
                print("Original eway_no:", eway_no)

                for i in range(len(eway_no) - 1, -1, -1):
                    if eway_no[i].isdigit():
                        # Increment the last digit by 1
                        new_digit = str((int(eway_no[i]) + 1) % 10)

                        # Replace the last digit in the input string
                        result = eway_no[:i] + new_digit + eway_no[i+1:]
                        print("Modified eway_no:", result)

                        # Break out of the loop after updating the last digit
                        break
        # if lastEstmate:
        #     Est_no = str(lastEstmate.challan_no)
        #     numbers = []
        #     stri = []
        #     for word in Est_no:
        #         if word.isdigit():
        #             numbers.append(word)
        #         else:
        #             stri.append(word)
            
        #     num=''
        #     for i in numbers:
        #         num +=i
            
        #     st = ''
        #     for j in stri:
        #         st = st+j

            # est_num = int(num)+1

            # if num[0] == '0':
            #     if est_num <10:
            #         nxtEstNo = st+'0'+ str(est_num)
            #     else:
            #         nxtEstNo = st+ str(est_num)
            # else:
        nxtEstNo = result

        PatternStr = result
        # for word in EstNo:
        #     if word.isdigit():
        #         pass
        #     else:
        #         PatternStr.append(word)
        
        pattern = ''
        for j in PatternStr:
            pattern += j

        pattern_exists = checkEstimateNumberPattern(pattern)

        if pattern !="" and pattern_exists:
            return JsonResponse({'status':False, 'message':'Challan No. Pattern already Exists.!'})
        elif Fin_Estimate.objects.filter(Company = com, estimate_no__iexact = EstNo).exists():
            return JsonResponse({'status':False, 'message':'Challan No. already Exists.!'})
        elif nxtEstNo != "" and EstNo != nxtEstNo:
            return JsonResponse({'status':False, 'message':'Challan No. is not continuous.!'})
        else:
            return JsonResponse({'status':True, 'message':'Number is okay.!'})
    else:
       return redirect('/')


def customer_dropdown(request):                                                                 #new by tinto mt (item)
    sid = request.session['s_id']
    login = Fin_Login_Details.objects.get(id=sid)
    if login.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = sid)
            options = {}
            option_objects = Fin_Customers.objects.filter(company=com)
            print(1111)
            for option in option_objects:
                title=option.title
                first_name=option.first_name
                last_name=option.last_name
                options[option.id] = [title,first_name,last_name,f"{title}"]
            return JsonResponse(options)
    elif login.User_Type == 'Staff':
            staf = Fin_Staff_Details.objects.get(Login_Id = sid)
            options = {}
            option_objects = Fin_Customers.objects.filter(company=staf.company_id)
            for option in option_objects:
                title=option.title
                first_name=option.first_name
                last_name=option.last_name
                options[option.id] = [title,first_name,last_name,f"{title}"]
            return JsonResponse(options)
    



# updated


def Fin_convertchallanToInvoice(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            cmp = com
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            cmp = com.company_id

        est = Fin_Delivery_Challan.objects.get(id = id)
        estItms = Fin_Delivery_Challan_Items.objects.filter(delivery_challan = est)
        cust = Fin_Customers.objects.filter(Company = cmp, status = 'Active')
        itms = Fin_Items.objects.filter(Company = cmp, status = 'Active')
        trms = Fin_Company_Payment_Terms.objects.filter(Company = cmp)
        bnk = Fin_Banking.objects.filter(company = cmp)
        lst = Fin_Price_List.objects.filter(Company = cmp, status = 'Active')
        units = Fin_Units.objects.filter(Company = cmp)
        acc = Fin_Chart_Of_Account.objects.filter(Q(account_type='Expense') | Q(account_type='Other Expense') | Q(account_type='Cost Of Goods Sold'), Company=cmp).order_by('account_name')

        # Fetching last invoice and assigning upcoming ref no as current + 1
        # Also check for if any bill is deleted and ref no is continuos w r t the deleted invoice
        latest_inv = Fin_Invoice.objects.filter(Company = cmp).order_by('-id').first()

        new_number = int(latest_inv.reference_no) + 1 if latest_inv else 1

        if Fin_Invoice_Reference.objects.filter(Company = cmp).exists():
            deleted = Fin_Invoice_Reference.objects.get(Company = cmp)
            
            if deleted:
                while int(deleted.reference_no) >= new_number:
                    new_number+=1

        # Finding next invoice number w r t last invoic number if exists.
        nxtInv = ""
        lastInv = Fin_Invoice.objects.filter(Company = cmp).last()
        if lastInv:
            inv_no = str(lastInv.invoice_no)
            numbers = []
            stri = []
            for word in inv_no:
                if word.isdigit():
                    numbers.append(word)
                else:
                    stri.append(word)
            
            num=''
            for i in numbers:
                num +=i
            
            st = ''
            for j in stri:
                st = st+j

            inv_num = int(num)+1

            if num[0] == '0':
                if inv_num <10:
                    nxtInv = st+'0'+ str(inv_num)
                else:
                    nxtInv = st+ str(inv_num)
            else:
                nxtInv = st+ str(inv_num)

        context = {
            'allmodules':allmodules, 'com':com, 'cmp':cmp, 'data':data,'estimate':est, 'estItems':estItms, 'customers':cust, 'items':itms, 'pTerms':trms,'list':lst,
            'banks':bnk,'units':units, 'accounts':acc,'ref_no':new_number,'invNo':nxtInv
        }
        return render(request,'company/Fin_Convert_Delivery_Challan_toInvoice.html',context)
    else:
       return redirect('/')

def newdeliverychallan(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        try:
            data = Fin_Login_Details.objects.get(id=s_id)
            if data.User_Type == "Company":
                com = Fin_Company_Details.objects.get(Login_Id=data)
                cmp = com
                allmodules = Fin_Modules_List.objects.get(Login_Id=s_id, status='New')
                
                cust = Fin_Customers.objects.filter(Company=com, status='Active')
                itms = Fin_Items.objects.filter(Company=com, status='Active')
                units = Fin_Units.objects.filter(Company=com)
                acc = Fin_Chart_Of_Account.objects.filter(Q(account_type='Expense') | Q(account_type='Other Expense') | Q(account_type='Cost Of Goods Sold'), Company=com).order_by('account_name')
                lst = Fin_Price_List.objects.filter(Company=com, status='Active')
                
                trms = Fin_Company_Payment_Terms.objects.filter(Company = com)
            else:
                com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
                cmp = com
                allmodules = Fin_Modules_List.objects.get(company_id=com.id, status='New')
                
                cust = Fin_Customers.objects.filter(Company=com.id, status='Active')
                itms = Fin_Items.objects.filter(Company=com.id, status='Active')
                units = Fin_Units.objects.filter(Company=com.id)
                acc = Fin_Chart_Of_Account.objects.filter(Q(account_type='Expense') | Q(account_type='Other Expense') | Q(account_type='Cost Of Goods Sold'), Company=com.id).order_by('account_name')
                lst = Fin_Price_List.objects.filter(Company=com.id, status='Active')
                
                trms = Fin_Company_Payment_Terms.objects.filter(Company = com.id)


            latest_eway = Fin_Delivery_Challan.objects.filter(Company=com).order_by('-reference_no').first()

            new_number = int(latest_eway.reference_no) + 1 if latest_eway else 1

            if Fin_Delivery_Challan_Reference.objects.filter(Company=com).exists():
                deleted = Fin_Delivery_Challan_Reference.objects.filter(Company=com).last()
                
                if deleted:
                    while int(deleted.reference_number) >= new_number:
                        new_number += 1

            nxtEway = ""
            lastEway = Fin_Delivery_Challan.objects.filter(Company=com).last()
            if lastEway:
                eway_no = str(lastEway.challan_no)
                print("Original eway_no:", eway_no)

                for i in range(len(eway_no) - 1, -1, -1):
                    if eway_no[i].isdigit():
                        # Increment the last digit by 1
                        new_digit = str((int(eway_no[i]) + 1) % 10)

                        # Replace the last digit in the input string
                        result = eway_no[:i] + new_digit + eway_no[i+1:]
                        print("Modified eway_no:", result)

                        # Break out of the loop after updating the last digit
                        break

                numbers = []
                stri = []




                # for word in eway_no:
                #     if word.isdigit():
                #         numbers.append(word)
                #     else:
                #         stri.append(word)

                # num = ''.join(numbers)
                # print(num)
                # st = ''.join(stri)
                # print(st)

                # eway_num = int(num) + 1
                
                # print(eway_num)
                # if num[0] == '0':
                #     nxtEway = st + '0' + str(eway_num)
                # else:
                nxtEway = result

            context = {
                'com': cmp,
                'LoginDetails': data,
                'allmodules': allmodules,
                'data': data,
                'com':com,
                
                'customers': cust,
                'items': itms,
                'lst': lst,
                'ESTNo':nxtEway,
              
                'pTerms':trms,
                'accounts':acc,
                'units':units,
                'ref_no':new_number
            }
            return render(request, 'company/Fin_add_delivery_challan.html', context)
        except Fin_Login_Details.DoesNotExist:
            return redirect('/')
    return redirect('newdeliverychallan')




# update 2

def createdeliverychallan(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        if request.method == 'POST':
            CHNo = request.POST['challan_no']

            PatternStr = []
            for word in CHNo:
                if word.isdigit():
                    pass
                else:
                    PatternStr.append(word)
            
            pattern = ''
            for j in PatternStr:
                pattern += j

            pattern_exists = checkEstimateNumberPattern(pattern)

            if pattern !="" and pattern_exists:
                res = f'<script>alert("Challan No. Pattern already Exists.! Try another!");window.history.back();</script>'
                return HttpResponse(res)

            if Fin_Delivery_Challan.objects.filter(Company = com, challan_no__iexact = CHNo).exists():
                res = f'<script>alert("Challan Number `{CHNo}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)
            
            challan = Fin_Delivery_Challan(
                Company = com,
                LoginDetails = com.Login_Id,
                Customer = None if request.POST['customer'] == "" else Fin_Customers.objects.get(id = request.POST['customer']),
                customer_email = request.POST['customerEmail'],
                billing_address = request.POST['bill_address'],
                gst_type = request.POST['gst_type'],
                gstin = request.POST['gstin'],
                place_of_supply = request.POST['place_of_supply'],
                reference_no = request.POST['reference_number'],
                challan_no = CHNo,
                challan_type= request.POST['challan_type'],
                
                challan_date = request.POST['challan_date'],
                # document= request.POST['file'],
                
                subtotal = 0.0 if request.POST['subtotal'] == "" else float(request.POST['subtotal']),
                igst = 0.0 if request.POST['igst'] == "" else float(request.POST['igst']),
                cgst = 0.0 if request.POST['cgst'] == "" else float(request.POST['cgst']),
                sgst = 0.0 if request.POST['sgst'] == "" else float(request.POST['sgst']),
                tax_amount = 0.0 if request.POST['taxamount'] == "" else float(request.POST['taxamount']),
                adjustment = 0.0 if request.POST['adj'] == "" else float(request.POST['adj']),
                shipping_charge = 0.0 if request.POST['ship'] == "" else float(request.POST['ship']),
                grandtotal = 0.0 if request.POST['grandtotal'] == "" else float(request.POST['grandtotal']),
                note = request.POST['note']
            )

            challan.save()
            challanref = Fin_Delivery_Challan_Reference(
                Company = com,
                LoginDetails = com.Login_Id,
                
                reference_number = request.POST['reference_number'],
                
            )

            challanref.save()



            if len(request.FILES) != 0:
                challan.document=request.FILES.get('file')
            challan.save()

            if 'Draft' in request.POST:
                challan.status = "Draft"
            elif "Save" in request.POST:
                challan.status = "Saved" 
            challan.save()

            # Save Estimate items.

            itemId = request.POST.getlist("item_id[]")
            itemName = request.POST.getlist("item_name[]")
            hsn  = request.POST.getlist("hsn[]")
            qty = request.POST.getlist("qty[]")
            price = request.POST.getlist("price[]")
            tax = request.POST.getlist("taxGST[]") if request.POST['place_of_supply'] == com.State else request.POST.getlist("taxIGST[]")
            discount = request.POST.getlist("discount[]")
            total = request.POST.getlist("total[]")

            if len(itemId)==len(itemName)==len(hsn)==len(qty)==len(price)==len(tax)==len(discount)==len(total) and itemId and itemName and hsn and qty and price and tax and discount and total:
                mapped = zip(itemId,itemName,hsn,qty,price,tax,discount,total)
                mapped = list(mapped)
                for ele in mapped:
                    itm = Fin_Items.objects.get(id = int(ele[0]))
                    created_instance = Fin_Delivery_Challan_Items.objects.create(delivery_challan = challan, items = itm, hsn = ele[2], quantity = int(ele[3]),  tax_rate = ele[5], discount = float(ele[6]), total = float(ele[7]))
                    itm.current_stock -= int(ele[3])
                    created_instance.save()
                    itm.save()
            
            # Save transaction
                    
            Fin_Delivery_Challan_History.objects.create(
                Company = com,
                LoginDetails = data,
                delivery_challan = challan,
                date=timezone.now().date(),
                
               
                action = 'Created'
            )

            return redirect(deliverylist)
        else:
            return redirect(deliverylist)
    else:
       return redirect('/')




def Fin_getItems2(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        items = {}
        option_objects = Fin_Items.objects.filter(Company = com, status='Active')
        for option in option_objects:
            items[option.name] = [option.name]

        return JsonResponse(items)
    else:
        return redirect('/')




def Fin_getInvItemDetails2(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        itemName = request.GET['item']
        print(itemName)
        # priceListId = request.GET['listId']
        item = Fin_Items.objects.get(Company = com, name = itemName)

        # if priceListId != "":
        #     priceList = Fin_Price_List.objects.get(id = int(priceListId))

        #     if priceList.item_rate == 'Customized individual rate':
        #         try:
        #             priceListPrice = float(Fin_PriceList_Items.objects.get(Company = com, list = priceList, item = item).custom_rate)
        #         except:
        #             priceListPrice = item.selling_price
        #     else:
        #         mark = priceList.up_or_down
        #         percentage = float(priceList.percentage)
        #         roundOff = priceList.round_off

        #         if mark == 'Markup':
        #             price = float(item.selling_price) + float((item.selling_price) * (percentage/100))
        #         else:
        #             price = float(item.selling_price) - float((item.selling_price) * (percentage/100))

        #         if priceList.round_off != 'Never mind':
        #             if roundOff == 'Nearest whole number':
        #                 finalPrice = round(price)
        #             else:
        #                 finalPrice = int(price) + float(roundOff)
        #         else:
        #             finalPrice = price

        #         priceListPrice = finalPrice
        # else:
        #     priceListPrice = None

        context = {
            'status':True,
            'id': item.id,
            'hsn':item.hsn,
            'sales_rate':item.selling_price,
            'purchase_rate':item.purchase_price,
            'avl':item.current_stock,
            'tax': True if item.tax_reference == 'taxable' else False,
            'gst':item.intra_state_tax,
            'igst':item.inter_state_tax,
            # 'PLPrice':priceListPrice,

        }
        return JsonResponse(context)
    else:
       return redirect('/')



def editchallan(request,id):
     if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        est = Fin_Delivery_Challan.objects.get(id = id)
        if request.method == 'POST':
            ESTNo = request.POST['challan_no']

            PatternStr = []
            for word in ESTNo:
                if word.isdigit():
                    pass
                else:
                    PatternStr.append(word)
            
            pattern = ''
            for j in PatternStr:
                pattern += j

            pattern_exists = checkEstimateNumberPattern(pattern)

            if pattern !="" and pattern_exists:
                res = f'<script>alert("Challan No. Pattern already Exists.! Try another!");window.history.back();</script>'
                return HttpResponse(res)

            if est.challan_no != ESTNo and Fin_Delivery_Challan.objects.filter(Company = com, challan_no__iexact = ESTNo).exists():
                res = f'<script>alert("Challan Number `{ESTNo}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)

            est.Customer = None if request.POST['customer'] == "" else Fin_Customers.objects.get(id = request.POST['customer'])
            est.customer_email = request.POST['customerEmail']
            est.billing_address = request.POST['bill_address']
            est.gst_type = request.POST['gst_type']
            est.gstin = request.POST['gstin']
            est.place_of_supply = request.POST['place_of_supply']

            est.challan_no = ESTNo
           
            est.challan_date = request.POST['challan_date']
            est.challan_type = request.POST['challan_type']
           

            est.subtotal = 0.0 if request.POST['subtotal'] == "" else float(request.POST['subtotal'])
            # est.igst = 0.0 if request.POST['igst'] == "" else float(request.POST['igst'])
            # est.cgst = 0.0 if request.POST['cgst'] == "" else float(request.POST['cgst'])
            # est.sgst = 0.0 if request.POST['sgst'] == "" else float(request.POST['sgst'])
            est.tax_amount = 0.0 if request.POST['taxamount'] == "" else float(request.POST['taxamount'])
            est.adjustment = 0.0 if request.POST['adj'] == "" else float(request.POST['adj'])
            est.shipping_charge = 0.0 if request.POST['ship'] == "" else float(request.POST['ship'])
            est.grandtotal = 0.0 if request.POST['grandtotal'] == "" else float(request.POST['grandtotal'])

            est.note = request.POST['note']

            if len(request.FILES) != 0:
                est.file=request.FILES.get('file')

            est.save()

            # Save estimate items.

            itemId = request.POST.getlist("item_id[]")
            itemName = request.POST.getlist("item_name[]")
            print(itemName)
            hsn  = request.POST.getlist("hsn[]")
            qty = request.POST.getlist("qty[]")
            price = request.POST.getlist("price[]")
            plc=request.POST['place_of_supply']

            cgst=request.POST.getlist("taxGST[]")
            igst=request.POST.getlist("taxIGST[]")

            if plc!=com.State:
                    tax = igst
                    est.igst = float(request.POST['igst'])
                    est.cgst = 0
                    est.sgst = 0
                    est.save()

            if plc==com.State:
                    tax = cgst
                    est.igst = 0
                    est.cgst = float(request.POST['cgst'])
                    est.sgst = float(request.POST['sgst'])
                    d = float(request.POST['cgst'])
                   
                    est.save()

             

            # tax = request.POST.getlist("taxGST[]") if request.POST['place_of_supply'] == com.State else request.POST.getlist("taxIGST[]")
            discount = request.POST.getlist("discount[]")
            total = request.POST.getlist("total[]")
            est_item_ids = request.POST.getlist("id[]")
            EstItem_ids = [int(id) for id in est_item_ids]

            estimate_items = Fin_Delivery_Challan_Items.objects.filter(delivery_challan = est)
            object_ids = [obj.id for obj in estimate_items]

            ids_to_delete = [obj_id for obj_id in object_ids if obj_id not in EstItem_ids]

            Fin_Delivery_Challan_Items.objects.filter(id__in=ids_to_delete).delete()
            
            count = Fin_Delivery_Challan_Items.objects.filter(delivery_challan = est).count()

            if len(itemId)==len(itemName)==len(hsn)==len(qty)==len(price)==len(tax)==len(discount)==len(total)==len(EstItem_ids) and EstItem_ids and itemId and itemName and hsn and qty and price and tax and discount and total:
                mapped = zip(itemId,itemName,hsn,qty,price,tax,discount,total,EstItem_ids)
                mapped = list(mapped)
                for ele in mapped:
                    if int(len(itemId))>int(count):
                        if ele[8] == 0:
                            itm = Fin_Items.objects.get(id = int(ele[0]))
                            Fin_Delivery_Challan_Items.objects.create(delivery_challan = est, items = itm, hsn = ele[2], quantity = int(ele[3]), price = ele[4],  tax_rate = ele[5], discount = float(ele[6]), total = float(ele[7]))
                            itm.current_stock -= int(ele[3])
                            # created_instance.save()
                            itm.save()
                        else:
                            itm = Fin_Items.objects.get(id = int(ele[0]))
                            Fin_Delivery_Challan_Items.objects.filter( id = int(ele[8])).update(delivery_challan = est, items = itm, hsn = ele[2], quantity = int(ele[3]), price = ele[4],  tax_rate = ele[5], discount = float(ele[6]), total = float(ele[7]))
                            itm.current_stock -= int(ele[3])
                            # created_instance.save()
                            itm.save()
                    else:
                        itm = Fin_Items.objects.get(id = int(ele[0]))
                        Fin_Delivery_Challan_Items.objects.filter( id = int(ele[8])).update(delivery_challan = est, items = itm, hsn = ele[2], quantity = int(ele[3]), price = ele[4],  tax_rate = ele[5], discount = float(ele[6]), total = float(ele[7]))
                        itm.current_stock -= int(ele[3])
                            # created_instance.save()
                        itm.save()
            # Save transaction
                    
            Fin_Delivery_Challan_History.objects.create(
                Company = com,
                LoginDetails = data,
                delivery_challan = est,
                date=timezone.now().date(),
                action = 'Edited'
            )

            return redirect(challan_overview, id)
        else:
            return redirect(challan_overview, id)
   


# debit note view tinto mt
        


def Fin_debitnotelist(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            cmp = com
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            cmp = com.company_id
        
        allmodules = Fin_Modules_List.objects.get(company_id = cmp,status = 'New')
        deli = Fin_Debit_Note.objects.filter(Company = cmp)
        return render(request,'company/Fin_Debit_Note_List.html',{'allmodules':allmodules,'com':com, 'cmp':cmp,'data':data,'deli':deli})
    else:
       return redirect('/')
     
    

def Fin_debitnoteadd(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        try:
            data = Fin_Login_Details.objects.get(id=s_id)
            if data.User_Type == "Company":
                com = Fin_Company_Details.objects.get(Login_Id=data)
                cmp = com
                allmodules = Fin_Modules_List.objects.get(Login_Id=s_id, status='New')
                
                vend = Fin_Vendors.objects.filter(Company=com, status='Active')
                itms = Fin_Items.objects.filter(Company=com, status='Active')
                units = Fin_Units.objects.filter(Company=com)
                banks = Fin_Banking.objects.filter(company=com)
                acc = Fin_Chart_Of_Account.objects.filter(Q(account_type='Expense') | Q(account_type='Other Expense') | Q(account_type='Cost Of Goods Sold'), Company=com).order_by('account_name')
                lst = Fin_Price_List.objects.filter(Company=com, status='Active')
                # recbill=Fin_Recurring_Bills.objects.filter(company=com)
            
                trms = Fin_Company_Payment_Terms.objects.filter(Company = com)
            else:
                com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
                cmp = com
                allmodules = Fin_Modules_List.objects.get(company_id=com.id, status='New')
                banks = Fin_Banking.objects.filter(company=com.id)
                vend = Fin_Vendors.objects.filter(Company=com.id, status='Active')
                itms = Fin_Items.objects.filter(Company=com.id, status='Active')
                units = Fin_Units.objects.filter(Company=com.id)
                acc = Fin_Chart_Of_Account.objects.filter(Q(account_type='Expense') | Q(account_type='Other Expense') | Q(account_type='Cost Of Goods Sold'), Company=com.id).order_by('account_name')
                lst = Fin_Price_List.objects.filter(Company=com.id, status='Active')
                # recbill=Fin_Recurring_Bills.objects.filter(Company=com.id)

                trms = Fin_Company_Payment_Terms.objects.filter(Company = com.id)


            latest_eway = Fin_Debit_Note.objects.filter(Company=com).order_by('-reference_number').first()

            new_number = int(latest_eway.reference_number) + 1 if latest_eway else 1

            if Fin_Debite_Note_Reference.objects.filter(Company=com).exists():
                deleted = Fin_Debite_Note_Reference.objects.filter(Company=com).last()
                
                if deleted:
                    while int(deleted.reference_number) >= new_number:
                        new_number += 1

            nxtEway = ""
            lastEway = Fin_Debit_Note.objects.filter(Company=com).last()
            if lastEway:
                eway_no = str(lastEway.debit_note_number)
                print("Original eway_no:", eway_no)

                for i in range(len(eway_no) - 1, -1, -1):
                    if eway_no[i].isdigit():
                        # Increment the last digit by 1
                        new_digit = str((int(eway_no[i]) + 1) % 10)

                        # Replace the last digit in the input string
                        result = eway_no[:i] + new_digit + eway_no[i+1:]
                        print("Modified eway_no:", result)

                        # Break out of the loop after updating the last digit
                        break

                numbers = []
                stri = []


                nxtEway = result

            context = {
                'com': cmp,
                'LoginDetails': data,
                'allmodules': allmodules,
                'data': data,
                'com':com,
                
                'venders': vend,
                'items': itms,
                'lst': lst,
                'ESTNo':nxtEway,
                # 'recbill':recbill,
                'banks':banks,
              
                'pTerms':trms,
                'accounts':acc,
                'units':units,
                'ref_no':new_number
            }
            return render(request, 'company/Fin_Debit_Note_Add.html', context)
        except Fin_Login_Details.DoesNotExist:
            return redirect('/')
    return redirect('Fin_debitnotelist')


def vendordata(request):
    sid = request.session['s_id']
    login = Fin_Login_Details.objects.get(id=sid)
    
    if login.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        customer_id = request.GET.get('id')
        print(customer_id)
        cust = Fin_Vendors.objects.get(id=customer_id,Company_id=com.id)
  
        recbill = Fin_Recurring_Bills.objects.filter(vendor=customer_id, company_id=com.id)
        purbill = Fin_Purchase_Bill.objects.filter(vendor=customer_id, company_id=com.id)

        recbill_data = [{'id': bill.id, 'bill_number': bill.bill_number} for bill in recbill]
        purbill_data = [{'id': bill.id, 'bill_number': bill.bill_no} for bill in purbill]

        # Combine recbill_data and purbill_data
        combined_data = recbill_data + purbill_data

        # Now you can use combined_data, which contains either recurring bills or purchase bills
        for data in combined_data:
            print(data['bill_number'])


        # Other customer information
        data7 = {
      
            'recbill_data': combined_data,
        }

        # Combine both sets of data
        combined_data = {'recbill_data': combined_data,      'email': cust.email,
            'billing_street': cust.billing_street,
            'billing_city': cust.billing_city,
            'billing_state': cust.billing_state,
            'gst_type': cust.gst_type,
            'gstin': cust.gstin,
            'place_of_supply': cust.place_of_supply, 'customer_data': data7}

        # Return JsonResponse with the combined data
        return JsonResponse(combined_data)
      
       
    elif login.User_Type == 'Staff' :
        staf = Fin_Staff_Details.objects.get(Login_Id = sid)
        customer_id = request.GET.get('id')
        print(customer_id)
        cust = Fin_Vendors.objects.get(id=customer_id,Company_id= staf.company_id_id)
  
        recbill = Fin_Recurring_Bills.objects.filter(vendor=customer_id, company_id= staf.company_id_id)
        purbill = Fin_Purchase_Bill.objects.filter(vendor=customer_id, company_id= staf.company_id_id)

        recbill_data = [{'id': bill.id, 'bill_number': bill.bill_number} for bill in recbill]
        purbill_data = [{'id': bill.id, 'bill_number': bill.bill_no} for bill in purbill]

        # Combine recbill_data and purbill_data
        combined_data = recbill_data + purbill_data

        # Now you can use combined_data, which contains either recurring bills or purchase bills
        for data in combined_data:
            print(data['bill_number'])


        # Other customer information
        data7 = {
      
            'recbill_data': combined_data,
        }

        # Combine both sets of data
        combined_data = {'recbill_data': combined_data,      'email': cust.email,
            'billing_street': cust.billing_street,
            'billing_city': cust.billing_city,
            'billing_state': cust.billing_state,
            'gst_type': cust.gst_type,
            'gstin': cust.gstin,
            'place_of_supply': cust.place_of_supply, 'customer_data': data7}

        # Return JsonResponse with the combined data
        return JsonResponse(combined_data)


def Fin_newdebitnote(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        if request.method == 'POST':
            CHNo = request.POST['debit_no']
            vendorid = request.POST['vendor']
            print(vendorid+"gg")
            vid=Fin_Vendors.objects.get(id=vendorid)
            # PatternStr = []
            # for word in CHNo:
            #     if word.isdigit():
            #         pass
            #     else:
            #         PatternStr.append(word)
            
            # pattern = ''
            # for j in PatternStr:
            #     pattern += j

            # pattern_exists = checkEstimateNumberPattern(pattern)

            # if pattern !="" and pattern_exists:
            #     res = f'<script>alert("Challan No. Pattern already Exists.! Try another!");window.history.back();</script>'
            #     return HttpResponse(res)

            # if Fin_Delivery_Challan.objects.filter(Company = com, challan_no__iexact = CHNo).exists():
            #     res = f'<script>alert("Challan Number `{CHNo}` already exists, try another!");window.history.back();</script>'
            #     return HttpResponse(res)
            
            debit = Fin_Debit_Note(
                Company = com,
                LoginDetails = com.Login_Id,
                Vendor = vid,
                vendor_email = request.POST['customerEmail'],
                billing_address = request.POST['bill_address'],
                gst_type = request.POST['gst_type'],
                gstin = request.POST['gstin'],
                place_of_supply = request.POST['place_of_supply'],
                reference_number = request.POST['reference_number'],
                debit_note_number = CHNo,
                bill_number= request.POST['billSelect'],
                
                debit_note_date = request.POST['debit_date'],
                payment_type = None if request.POST['payment_method'] == "" else request.POST['payment_method'],
                cheque_number = None if request.POST['cheque_id'] == "" else request.POST['cheque_id'],
                upi_id = None if request.POST['upi_id'] == "" else request.POST['upi_id'],
                bank_account = None if request.POST['bnk_id'] == "" else request.POST['bnk_id'],
                document= request.POST['file'],
                
                subtotal = 0.0 if request.POST['subtotal'] == "" else float(request.POST['subtotal']),
                igst = 0.0 if request.POST['igst'] == "" else float(request.POST['igst']),
                cgst = 0.0 if request.POST['cgst'] == "" else float(request.POST['cgst']),
                sgst = 0.0 if request.POST['sgst'] == "" else float(request.POST['sgst']),
                tax_amount = 0.0 if request.POST['taxamount'] == "" else float(request.POST['taxamount']),
                adjustment = 0.0 if request.POST['adj'] == "" else float(request.POST['adj']),
                shipping_charge = 0.0 if request.POST['ship'] == "" else float(request.POST['ship']),
                grandtotal = 0.0 if request.POST['grandtotal'] == "" else float(request.POST['grandtotal']),
                note = request.POST['note'],
                paid=0.0 if request.POST['advance'] == "" else float(request.POST['advance']),
                balance=0.0 if request.POST['balance'] == "" else float(request.POST['balance'])
                )

            debit.save()
            challanref = Fin_Debite_Note_Reference(
                Company = com,
                LoginDetails = com.Login_Id,
                debit_note=debit,
                
                reference_number = request.POST['reference_number'],
                
            )

            challanref.save()



            # if len(request.FILES) != 0:
            #     challan.document=request.FILES.get('file')
            # challan.save()

            if 'Draft' in request.POST:
                debit.status = "Draft"
            elif "Save" in request.POST:
                debit.status = "Saved" 
            debit.save()

            # # Save Estimate items.

            itemId = request.POST.getlist("item_id[]")
            itemName = request.POST.getlist("item_name[]")
            hsn  = request.POST.getlist("hsn[]")
            qty = request.POST.getlist("qty[]")
            price = request.POST.getlist("price[]")
            tax = request.POST.getlist("taxGST[]") if request.POST['place_of_supply'] == com.State else request.POST.getlist("taxIGST[]")
            discount = request.POST.getlist("discount[]")
            total = request.POST.getlist("total[]")

            if len(itemId)==len(itemName)==len(hsn)==len(qty)==len(price)==len(tax)==len(discount)==len(total) and itemId and itemName and hsn and qty and price and tax and discount and total:
                mapped = zip(itemId,itemName,hsn,qty,price,tax,discount,total)
                mapped = list(mapped)
                for ele in mapped:
                    itm = Fin_Items.objects.get(id = int(ele[0]))
                    created_instance = Fin_Debit_Note_Items.objects.create(debit_note = debit, items = itm, hsn = ele[2], quantity = int(ele[3]),  tax_rate = ele[5], discount = float(ele[6]), total = float(ele[7]))
                    itm.current_stock -= int(ele[3])
                    created_instance.save()
                    itm.save()
            
            # # Save transaction
                    
            Fin_Debite_Note_History.objects.create(
                Company = com,
                LoginDetails = data,
                debit_note = debit,
                date=timezone.now().date(),
                
               
                action = 'Created'
            )

            return redirect(Fin_debitnotelist)
        else:
            return redirect(Fin_debitnotelist)
    else:
       return redirect('/')

def Fin_checkdebitNumber(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        EstNo = request.GET['EstNum']

        nxtEstNo = ""
        lastEstmate = Fin_Debit_Note.objects.filter(Company = com).last()
        # lastEstmate = Fin_Delivery_Challan.objects.filter(Company=com).last()
        if lastEstmate:
                eway_no = str(lastEstmate.debit_note_number)
                print("Original eway_no:", eway_no)

                for i in range(len(eway_no) - 1, -1, -1):
                    if eway_no[i].isdigit():
                        # Increment the last digit by 1
                        new_digit = str((int(eway_no[i]) + 1) % 10)

                        # Replace the last digit in the input string
                        result = eway_no[:i] + new_digit + eway_no[i+1:]
                        print("Modified eway_no:", result)

                        # Break out of the loop after updating the last digit
                        break
        # if lastEstmate:
        #     Est_no = str(lastEstmate.challan_no)
        #     numbers = []
        #     stri = []
        #     for word in Est_no:
        #         if word.isdigit():
        #             numbers.append(word)
        #         else:
        #             stri.append(word)
            
        #     num=''
        #     for i in numbers:
        #         num +=i
            
        #     st = ''
        #     for j in stri:
        #         st = st+j

            # est_num = int(num)+1

            # if num[0] == '0':
            #     if est_num <10:
            #         nxtEstNo = st+'0'+ str(est_num)
            #     else:
            #         nxtEstNo = st+ str(est_num)
            # else:
        nxtEstNo = result

        PatternStr = result
        # for word in EstNo:
        #     if word.isdigit():
        #         pass
        #     else:
        #         PatternStr.append(word)
        
        pattern = ''
        for j in PatternStr:
            pattern += j

        pattern_exists = checkEstimateNumberPattern(pattern)

        if pattern !="" and pattern_exists:
            return JsonResponse({'status':False, 'message':'Challan No. Pattern already Exists.!'})
        elif Fin_Estimate.objects.filter(Company = com, estimate_no__iexact = EstNo).exists():
            return JsonResponse({'status':False, 'message':'Challan No. already Exists.!'})
        elif nxtEstNo != "" and EstNo != nxtEstNo:
            return JsonResponse({'status':False, 'message':'Challan No. is not continuous.!'})
        else:
            return JsonResponse({'status':True, 'message':'Number is okay.!'})
    else:
       return redirect('/')


def billdata(request):
    sid = request.session['s_id']
    login = Fin_Login_Details.objects.get(id=sid)
    
    if login.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        itemname = request.GET.get('itemname')
        billnumber = request.GET.get('billnumber')
        print(billnumber)
        
        itm = Fin_Items.objects.get(name=itemname,Company_id=com.id)
        print(itm.name+"hh")
        pbill=Fin_Purchase_Bill.objects.get(bill_no=billnumber,company_id=com.id)
        if pbill is not None:
            pbillitem=Fin_Purchase_Bill_Item.objects.get(pbill=pbill,company_id=com.id,item=itm)
        else:
            rbill=Fin_Recurring_Bills.objects.get(bill_number=billnumber,company_id=com.id)
            pbillitem=Fin_Recurring_Bill_Items.objects.get(recurring_bill=rbill,company_id=com.id,item=itm)

        

        
       
        print(pbillitem.item.name)

        billitemqty=pbillitem.qty
        print(billitemqty)
        data7 = {'itemnames':pbillitem.item.name,'qty':billitemqty}
        return JsonResponse(data7)

      
        
    elif login.User_Type == 'Staff' :
        staf = Fin_Staff_Details.objects.get(Login_Id = sid)
        

        itemname = request.GET.get('itemname')
        billnumber = request.GET.get('billnumber')
        print(billnumber)
        
        itm = Fin_Items.objects.get(name=itemname,Company_id=staf.company_id_id)
        print(itm.name+"hh")
        pbill=Fin_Purchase_Bill.objects.get(bill_no=billnumber,company_id=staf.company_id_id)
        if pbill is not None:
            pbillitem=Fin_Purchase_Bill_Item.objects.get(pbill=pbill,company_id=staf.company_id_id,item=itm)
        else:
            rbill=Fin_Recurring_Bills.objects.get(bill_number=rbill,company_id=staf.company_id_id)
            pbillitem=Fin_Recurring_Bill_Items.objects.get(recurring_bill=billnumber,company_id=staf.company_id_id,item=itm)

        

        
       
        print(pbillitem.item.name)

        billitemqty=pbillitem.qty
        print(billitemqty)
        data7 = {'itemnames':pbillitem.item.name,'qty':billitemqty}
        return JsonResponse(data7)


def Fin_debit_overview(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)

        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            cmp = com
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            cmp = com.company_id
        
        allmodules = Fin_Modules_List.objects.get(company_id = cmp,status = 'New')
        Estimate = Fin_Debit_Note.objects.get(id = id)
        cmt = Fin_Debite_Note_Comments.objects.filter(debit_note = Estimate)
        hist = Fin_Debite_Note_History.objects.filter(debit_note = Estimate).last()
        EstItems = Fin_Debit_Note_Items.objects.filter(debit_note = Estimate)
        histpry = Fin_Debite_Note_History.objects.filter(debit_note = Estimate)
        try:
            created = Fin_Debite_Note_History.objects.get(debit_note = Estimate, action = 'Created')
        except:
            created = None
#  'comments':cmt, 
        return render(request,'company/Fin_Debit_Note_Overview.html',{'allmodules':allmodules,'com':com,'cmp':cmp, 'data':data, 'estimate':Estimate,'estItems':EstItems, 'history':hist,'created':created,'comments':cmt,'histpry2':histpry})
    else:
       return redirect('/')

def Fin_editdebitnote(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            cmp = com
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            cmp = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = cmp,status = 'New')
        est = Fin_Debit_Note.objects.get(id = id)
        estItms = Fin_Debit_Note_Items.objects.filter(debit_note = est)
        cust = Fin_Vendors.objects.filter(Company = cmp, status = 'Active')
        itms = Fin_Items.objects.filter(Company = cmp, status = 'Active')
        banks = Fin_Banking.objects.filter(company=com.id)
       
        context = {
            'allmodules':allmodules, 'com':com, 'cmp':cmp, 'data':data,'estimate':est, 'estItems':estItms, 'customers':cust, 'items':itms,'banks':banks
           
        }
        return render(request,'company/Fin_Debit_Note_Edit.html',context)
    else:
       return redirect('/')


def editdebit(request,id):
     if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        est = Fin_Debit_Note.objects.get(id = id)
        if request.method == 'POST':
            ESTNo = request.POST['debit_no']

            PatternStr = []
            for word in ESTNo:
                if word.isdigit():
                    pass
                else:
                    PatternStr.append(word)
            
            pattern = ''
            for j in PatternStr:
                pattern += j

            pattern_exists = checkEstimateNumberPattern(pattern)

            if pattern !="" and pattern_exists:
                res = f'<script>alert("Debit No. Pattern already Exists.! Try another!");window.history.back();</script>'
                return HttpResponse(res)

            if est.debit_note_number != ESTNo and Fin_Debit_Note.objects.filter(Company = com, debit_note_date__iexact = ESTNo).exists():
                res = f'<script>alert("Debit Number `{ESTNo}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)

            est.Vendor = None if request.POST['customer'] == "" else Fin_Vendors.objects.get(id = request.POST['customer'])
            est.vendor_email = request.POST['customerEmail']
            est.billing_address = request.POST['bill_address']
            est.gst_type = request.POST['gst_type']
            est.gstin = request.POST['gstin']
            est.place_of_supply = request.POST['place_of_supply']

            est.debit_note_number = ESTNo
           
            est.debit_note_date = request.POST['debit_date']
            est.payment_type = request.POST['payment_type']
            est.cheque_number = request.POST['cheque_id']
            est.upi_id = request.POST['upi_id']
            est.bank_account = request.POST['bnk_id']
           

            est.subtotal = 0.0 if request.POST['subtotal'] == "" else float(request.POST['subtotal'])
            # est.igst = 0.0 if request.POST['igst'] == "" else float(request.POST['igst'])
            # est.cgst = 0.0 if request.POST['cgst'] == "" else float(request.POST['cgst'])
            # est.sgst = 0.0 if request.POST['sgst'] == "" else float(request.POST['sgst'])
            est.tax_amount = 0.0 if request.POST['taxamount'] == "" else float(request.POST['taxamount'])
            est.adjustment = 0.0 if request.POST['adj'] == "" else float(request.POST['adj'])
            est.shipping_charge = 0.0 if request.POST['ship'] == "" else float(request.POST['ship'])
            est.grandtotal = 0.0 if request.POST['grandtotal'] == "" else float(request.POST['grandtotal'])

            est.note = request.POST['note']

            if len(request.FILES) != 0:
                est.file=request.FILES.get('file')

            est.save()

            # Save estimate items.

            itemId = request.POST.getlist("item_id[]")
            itemName = request.POST.getlist("item_name[]")
            print(itemName)
            hsn  = request.POST.getlist("hsn[]")
            qty = request.POST.getlist("qty[]")
            price = request.POST.getlist("price[]")
            plc=request.POST['place_of_supply']

            cgst=request.POST.getlist("taxGST[]")
            igst=request.POST.getlist("taxIGST[]")

            if plc!=com.State:
                    tax = igst
                    est.igst = float(request.POST['igst'])
                    est.cgst = 0
                    est.sgst = 0
                    est.save()

            if plc==com.State:
                    tax = cgst
                    est.igst = 0
                    est.cgst = float(request.POST['cgst'])
                    est.sgst = float(request.POST['sgst'])
                    d = float(request.POST['cgst'])
                   
                    est.save()

             

            # tax = request.POST.getlist("taxGST[]") if request.POST['place_of_supply'] == com.State else request.POST.getlist("taxIGST[]")
            discount = request.POST.getlist("discount[]")
            total = request.POST.getlist("total[]")
            est_item_ids = request.POST.getlist("id[]")
            EstItem_ids = [int(id) for id in est_item_ids]

            estimate_items = Fin_Debit_Note_Items.objects.filter(debit_note = est)
            object_ids = [obj.id for obj in estimate_items]

            ids_to_delete = [obj_id for obj_id in object_ids if obj_id not in EstItem_ids]

            Fin_Debit_Note_Items.objects.filter(id__in=ids_to_delete).delete()
            
            count = Fin_Debit_Note_Items.objects.filter(debit_note = est).count()

            if len(itemId)==len(itemName)==len(hsn)==len(qty)==len(price)==len(tax)==len(discount)==len(total)==len(EstItem_ids) and EstItem_ids and itemId and itemName and hsn and qty and price and tax and discount and total:
                mapped = zip(itemId,itemName,hsn,qty,price,tax,discount,total,EstItem_ids)
                mapped = list(mapped)
                for ele in mapped:
                    if int(len(itemId))>int(count):
                        if ele[8] == 0:
                            itm = Fin_Items.objects.get(id = int(ele[0]))
                            Fin_Debit_Note_Items.objects.create(debit_note = est, items = itm, hsn = ele[2], quantity = int(ele[3]), price = ele[4],  tax_rate = ele[5], discount = float(ele[6]), total = float(ele[7]))
                            itm.current_stock -= int(ele[3])
                            # created_instance.save()
                            itm.save()
                        else:
                            itm = Fin_Items.objects.get(id = int(ele[0]))
                            Fin_Debit_Note_Items.objects.filter( id = int(ele[8])).update(debit_note = est, items = itm, hsn = ele[2], quantity = int(ele[3]), price = ele[4],  tax_rate = ele[5], discount = float(ele[6]), total = float(ele[7]))
                            itm.current_stock -= int(ele[3])
                            # created_instance.save()
                            itm.save()
                    else:
                        itm = Fin_Items.objects.get(id = int(ele[0]))
                        Fin_Debit_Note_Items.objects.filter( id = int(ele[8])).update(debit_note = est, items = itm, hsn = ele[2], quantity = int(ele[3]), price = ele[4],  tax_rate = ele[5], discount = float(ele[6]), total = float(ele[7]))
                        itm.current_stock -= int(ele[3])
                            # created_instance.save()
                        itm.save()
            # Save transaction
                    
            Fin_Debite_Note_History.objects.create(
                Company = com,
                LoginDetails = data,
                debit_note = est,
                date=timezone.now().date(),
                action = 'Edited'
            )

            return redirect(Fin_debit_overview, id)
        else:
            return redirect(Fin_debit_overview, id)
   

def Fin_deletedebit(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        est = Fin_Debit_Note.objects.get( id = id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        Fin_Debit_Note_Items.objects.filter(debit_note = est).delete()

        # Storing ref number to deleted table
        # if entry exists and lesser than the current, update and save => Only one entry per company
        if Fin_Debite_Note_Reference.objects.filter(Company = com).exists():
            deleted = Fin_Debite_Note_Reference.objects.get(Company = com,debit_note=est)
            if int(est.reference_number) > int(deleted.reference_number):
                deleted.reference_number = est.reference_number
                deleted.save()
        else:
            Fin_Debite_Note_Reference.objects.create(Company = com, reference_number = est.reference_number)
        
        est.delete()
        return redirect(Fin_debitnotelist)

def Fin_adddebitComment(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id

        est = Fin_Debit_Note.objects.get(id = id)
        if request.method == "POST":
            cmt = request.POST['comment'].strip()

            Fin_Debite_Note_Comments.objects.create(Company = com, debit_note = est, comments = cmt)
            return redirect(Fin_debit_overview, id)
        return redirect(Fin_debit_overview, id)
    return redirect('/')


def Fin_deletedebitComment(request,id):
    if 's_id' in request.session:
        cmt = Fin_Debite_Note_Comments.objects.get(id = id)
        estId = cmt.debit_note.id
        cmt.delete()
        return redirect(Fin_debit_overview, estId)


def Fin_attachdebitFile(request, id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        est = Fin_Debit_Note.objects.get(id = id)

        if request.method == 'POST' and len(request.FILES) != 0:
            est.document = request.FILES.get('file')
            est.save()

        return redirect(Fin_debit_overview, id)
    else:
        return redirect('/')
   

def Fin_sharedebitToEmail(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id=s_id)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id).company_id
        
        est = Fin_Debit_Note.objects.get(id = id)
        itms = Fin_Debit_Note_Items.objects.filter(debit_note = est)
        try:
            if request.method == 'POST':
                emails_string = request.POST['email_ids']

                # Split the string by commas and remove any leading or trailing whitespace
                emails_list = [email.strip() for email in emails_string.split(',')]
                email_message = request.POST['email_message']
                print(emails_list)
            
                context = {'estimate':est, 'estItems':itms,'cmp':com}
                template_path = 'company/Fin_Debit_Note_Pdf.html'
                template = get_template(template_path)

                html  = template.render(context)
                result = BytesIO()
                pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
                pdf = result.getvalue()
                filename = f'Debit{est.debit_note_number}'
                subject = f"Debi_Note{est.debit_note_number}"
                email = EmailMessage(subject, f"Hi,\nPlease find the attached debit note for - #-{est.debit_note_number}. \n{email_message}\n\n--\nRegards,\n{com.Company_name}\n{com.Address}\n{com.State} - {com.Country}\n{com.Contact}", from_email=settings.EMAIL_HOST_USER, to=emails_list)
                email.attach(filename, pdf, "application/pdf")
                email.send(fail_silently=False)

                messages.success(request, 'Debit Note has been shared via email successfully..!')
                return redirect(Fin_debit_overview,id)
        except Exception as e:
            print(e)
            messages.error(request, f'{e}')
            return redirect(Fin_debit_overview, id)


def Fin_convertdebit(request,id):
    if 's_id' in request.session:

        est = Fin_Debit_Note.objects.get(id = id)
        est.status = 'Saved'
        est.save()
        return redirect(Fin_debit_overview, id)



def checkitem(request):
    sid = request.session['s_id']
    login = Fin_Login_Details.objects.get(id=sid)
    
    if login.User_Type == 'Company':
        com = Fin_Company_Details.objects.get(Login_Id = sid)
        itemname = request.GET.get('itemname')
        billnumber = request.GET.get('billnumber')
        print(billnumber)
        
        itm = Fin_Items.objects.get(name=itemname,Company_id=com.id)
        print(itm.name+"hh")
        pbill=Fin_Purchase_Bill.objects.get(bill_no=billnumber,company_id=com.id)
        # if pbill is not None:
        try:
            pbillitem = Fin_Purchase_Bill_Item.objects.get(pbill=pbill, company_id=com.id, item=itm)
            billitemqty=pbillitem.qty
            itmname=pbillitem.item.name
        except Fin_Purchase_Bill_Item.DoesNotExist:
            itmname = 0
            billitemqty=0

        #     print("null1")
        # else:
        #     rbill=Fin_Recurring_Bills.objects.get(bill_number=billnumber,company_id=com.id)
        #     pbillitem=Fin_Recurring_Bill_Items.objects.get(recurring_bill=rbill,company_id=com.id,item=itm)
        #     print("null2")
        # if pbillitem is  None:
        #     pbillitem=0
        #     print("null")

        

        
       
        # print(pbillitem.item.name)

        

        print("kkll")
        print(billitemqty)
        data7 = {'itemnames':itmname,'qty':billitemqty}
        return JsonResponse(data7)

      
        
    elif login.User_Type == 'Staff' :
        staf = Fin_Staff_Details.objects.get(Login_Id = sid)
        

        itemname = request.GET.get('itemname')
        billnumber = request.GET.get('billnumber')
        print(billnumber)
        
        itm = Fin_Items.objects.get(name=itemname,Company_id=staf.company_id_id)
        print(itm.name+"hh")
        pbill=Fin_Purchase_Bill.objects.get(bill_no=billnumber,company_id=staf.company_id_id)
        # if pbill is not None:
        try:
            pbillitem = Fin_Purchase_Bill_Item.objects.get(pbill=pbill, company_id=staf.company_id_id, item=itm)
            billitemqty=pbillitem.qty
            itmname=pbillitem.item.name
        except Fin_Purchase_Bill_Item.DoesNotExist:
            itmname = 0
            billitemqty=0

        #     print("null1")
        # else:
        #     rbill=Fin_Recurring_Bills.objects.get(bill_number=billnumber,company_id=com.id)
        #     pbillitem=Fin_Recurring_Bill_Items.objects.get(recurring_bill=rbill,company_id=com.id,item=itm)
        #     print("null2")
        # if pbillitem is  None:
        #     pbillitem=0
        #     print("null")

        

        
       
        # print(pbillitem.item.name)

        

        print("kkll")
        print(billitemqty)
        data7 = {'itemnames':itmname,'qty':billitemqty}
        return JsonResponse(data7)
