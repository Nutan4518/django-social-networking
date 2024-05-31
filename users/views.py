import jwt
from django.conf import settings
from .models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination

# from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import F, Func, Value

from datetime import datetime, timedelta
import random, string
from django.utils import timezone


# def validatedate(date_text):
#     try:
#         datetime.strptime(date_text, "%Y-%m-%d")
#         return True
#     except:
#         return False


def generate_token(id, name, email):
    payload = {
        "id": id,
        "name": name,
        "email": email,
        "exp": timezone.now() + timedelta(hours=24),
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS512")
    return token


def handle_auth_exceptions(func):
    def wrapper(*args, **kwargs):
        result = {}
        result["status"] = "NOK"
        result["valid"] = False
        result["result"] = {"message": "Unauthorized access", "data": {}}
        try:
            request = args[1]  # Assuming the request is the second argument
            header_access_token = request.META.get("HTTP_AUTHORIZATION")
            if not header_access_token:
                result["result"]["message"] = "Authorization header missing"
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
            splited_access_token = header_access_token.split(" ")
            if len(splited_access_token) != 2:
                result["result"]["message"] = "Authorization header missing"
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
            access_token = splited_access_token[1]
            Users_data = jwt.decode(
                access_token, settings.JWT_SECRET_KEY, algorithms=["HS512"]
            )
            if not Users_data or "email" not in Users_data:
                result["result"]["message"] = "Users data not found in token"
                return Response(result, status=status.HTTP_401_UNAUTHORIZED)
            request.Users_data = Users_data
            return func(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            result["result"]["message"] = "Token expired. Please login again"
            return Response(result, status=status.HTTP_401_UNAUTHORIZED)
        except Users.DoesNotExist:
            result["result"]["message"] = "Users not found"
            return Response(result, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            result["result"]["message"] = str(e)
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            result["result"]["message"] = str(e)
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return wrapper

# Api to register user
class RegisterUser(APIView):
    def post(self, request):
        result = {}
        result["status"] = "NOK"
        result["valid"] = False
        result["result"] = {"message": "Unauthorized access", "data": {}}

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            hashed_password = make_password(request.data["password"])
            serializer.validated_data["password"] = hashed_password
            serializer.save()
            result["status"] = "OK"
            result["valid"] = True
            result["result"]["message"] = "Users registered successfully"
            result["result"]["data"] = {
                "name": serializer.data["name"],
                "email": serializer.data["email"],
            }
            return Response(result, status=status.HTTP_200_OK)

        else:
            result["result"]["message"] = (
                list(serializer.errors.keys())[0]
                + " - "
                + list(serializer.errors.values())[0][0]
            ).capitalize()
            return Response(result, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


# Api to Login user
class LoginUser(APIView):
    def post(self, request):
        result = {}
        result["status"] = "NOK"
        result["valid"] = False
        result["result"] = {"message": "Unauthorized access", "data": {}}
        serializer = EmailLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]
            try:
                user_data = Users.objects.get(Q(email__iexact=email))
            except Exception as e:
                result["result"]["message"] = "User is Not Present"
                return Response(result, status=status.HTTP_401_UNAUTHORIZED)

            if user_data is None or user_data.is_active == 0:
                result["result"]["message"] = "Invalid username or password"
                return Response(result, status=status.HTTP_401_UNAUTHORIZED)
            else:

                if not check_password(password, user_data.password):
                    result["result"]["message"] = "Incorrect password"
                    return Response(result, status=status.HTTP_401_UNAUTHORIZED)

                token = generate_token(user_data.id, user_data.name, user_data.email)
                user_data.last_login = (timezone.now()).strftime("%Y-%m-%d %H:%M:%S")
                user_data.save()
                final_response = {
                    "id": user_data.id,
                    "name": user_data.name,
                    "last_login": user_data.last_login,
                    "token": token,
                }

            result["status"] = "OK"
            result["valid"] = True
            result["result"]["message"] = "You are successfully logged in."
            result["result"]["data"] = final_response
            return Response(result, status=status.HTTP_200_OK)
        else:
            result["result"]["message"] = (
                list(serializer.errors.keys())[0]
                + " - "
                + list(serializer.errors.values())[0][0]
            ).capitalize()
            return Response(result, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class SearchUser(APIView, PageNumberPagination):
    @handle_auth_exceptions
    def get(self, request, format=None):
        result = {}
        result["status"] = "NOK"
        result["valid"] = False
        result["result"] = {"message": "Unauthorized access", "data": {}}
        try:
            filter_object = Q()
            if (
                "search_string" in request.query_params
                and request.query_params["search_string"] != ""
            ):
                search_string = request.query_params.get("search_string")
                search_condition = Q(name__icontains=search_string) | Q(
                    email__iexact=search_string
                )
                filter_object &= search_condition
                filter_object &= Q(is_active=1)
                all_users = Users.objects.filter(filter_object).values()
                user_list = [user for user in all_users]

                paginated_data = self.paginate_queryset(user_list, request, view=self)
                paginated_data = self.get_paginated_response(paginated_data).data
                result["status"] = "OK"
                result["valid"] = True
                result["result"]["message"] = "Data fetched successfully"
                result["result"]["next"] = paginated_data["next"]
                result["result"]["previous"] = paginated_data["previous"]
                result["result"]["count"] = paginated_data["count"]
                result["result"]["data"] = paginated_data["results"]
                return Response(result, status=status.HTTP_200_OK)

            else:
                result["result"]["message"] = "Search string is required"
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            result["result"]["message"] = f"Error fetching data: {str(e)}"
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# API to send/accept/reject friend request
class SendRequest(APIView):
    @handle_auth_exceptions
    def post(self,request):
        result = {}
        result['status']    =   "NOK"
        result['valid']     =   False
        result['result']    =   {"message":"Unauthorized access","data":{}}
        try:
            user_data = request.Users_data
            user_id = user_data['id']  # Assuming 'id' is the key for the user ID in the payload
            from_user = Users.objects.get(id=user_id)
            to_user = request.data['to_user']
            to_user = Users.objects.get(email=to_user)
            
            if from_user == to_user:
                result['result']['message'] = "You cant send a friend request to yourself!!"
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

            one_minute_ago = timezone.now() - timedelta(minutes=1)
            request_count = Friends.objects.filter(
                from_user=from_user,
                to_user=to_user,
                requested_at__gte=one_minute_ago
            ).count()
            
            if request_count >= 3:
                result['result']['message'] = "You can't send more than three friend requests to this user in the last minute"
                return Response(result, status=status.HTTP_429_TOO_MANY_REQUESTS)

            
            friend_request = Friends(from_user=from_user, to_user=to_user, requested_at=timezone.now(), status='pending')
            friend_request.save()

            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = "Request sent successfully"
            return Response(result, status=status.HTTP_200_OK)
        except Users.DoesNotExist as e:
            result['result']['message'] = "user does not exist."
            return Response(result, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        
        except Exception as e:
                result['result']['message'] = str(e)
                return Response(result, status=status.HTTP_401_UNAUTHORIZED)




class AcceptRequest(APIView):
    @handle_auth_exceptions
    def post(self,request):
        result = {}
        result['status']    =   "NOK"
        result['valid']     =   False
        result['result']    =   {"message":"Unauthorized access","data":{}}
        try:     
            current_user=request.Users_data['id']
            from_user = request.data['from_user']
            from_user = Users.objects.get(email=from_user)
            pending_requests = Friends.objects.filter(from_user=from_user,to_user=current_user, status='pending').values()
            if not pending_requests.exists():
                result['result']['message'] = f"No pending request from {from_user}!!"
                return Response(result, status=status.HTTP_200_OK)

            pending_requests.update(status='accepted', accepted_at=timezone.now())
            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = f"Request from {from_user} is accepted."
            return Response(result, status=status.HTTP_200_OK)

        except Users.DoesNotExist:
            result['result']['message'] = "No request from this user exists."
            return Response(result, status=status.HTTP_404_NOT_FOUND)
        except Friends.DoesNotExist as e:
            result['result']['message'] = "friend request does not exist."
            return Response(result, status=status.HTTP_422_UNPROCESSABLE_ENTITY)      
        except Exception as e:
                result['result']['message'] = str(e)
                return Response(result, status=status.HTTP_401_UNAUTHORIZED)


class RejectFriendRequest(APIView):
    @handle_auth_exceptions
    def post(self,request):
        result = {}
        result['status']    =   "NOK"
        result['valid']     =   False
        result['result']    =   {"message":"Unauthorized access","data":{}}
        try:     
            current_user=request.Users_data['id']
            from_user = request.data['from_user']
            from_user = Users.objects.get(email=from_user)
            pending_requests = Friends.objects.filter(from_user=from_user.id, to_user=current_user, status='pending').values()
            # print("pending ",pending_requests)
            if not pending_requests.exists():
                result['result']['message'] = f"No pending request from {from_user}!!"
                return Response(result, status=status.HTTP_200_OK)

            pending_requests.update(status='rejected', rejected_at=timezone.now())
            result['status'] = "OK"
            result['valid'] = True
            result['result']['message'] = f"Request from {from_user} is rejected."
            return Response(result, status=status.HTTP_200_OK)
        except Users.DoesNotExist:
            result['result']['message'] = "No request from this user exists."
            return Response(result, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
                result['result']['message'] = str(e)
                return Response(result, status=status.HTTP_401_UNAUTHORIZED)


# Listing Apis to list pending/accepted and rejected requests
class FriendsList(APIView,PageNumberPagination):
    @handle_auth_exceptions
    def get(self,request):
        result = {}
        result['status']    =   "NOK"
        result['valid']     =   False
        result['result']    =   {"message":"Unauthorized access","data":{}}
        try:      
            from_user = request.Users_data
            friends_list = Friends.objects.filter(to_user=from_user['id'],status='accepted').values_list('from_user_id', flat=True).distinct()
            if not friends_list.exists():
                result['result']['message'] = " You don't have any Friends!!"
                return Response(result, status=status.HTTP_200_OK)

            friends_data = Users.objects.filter(id__in=friends_list).values('id', 'name')
            
            paginated_data = self.paginate_queryset(friends_data, request, view=self)
            paginated_data = self.get_paginated_response(paginated_data).data
            result['status']              = "OK"
            result['valid']               = True
            result['result']['message']   = "Data fetched successfully"
            result['result']['next']      = paginated_data['next']
            result['result']['previous']  = paginated_data['previous']
            result['result']['count']     = paginated_data['count']
            result['result']['data']      = paginated_data['results']
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
                result['result']['message'] = str(e)
                return Response(result, status=status.HTTP_401_UNAUTHORIZED)





class PendingRequestsList(APIView,PageNumberPagination):
    @handle_auth_exceptions
    def get(self,request):
        result = {}
        result['status']    =   "NOK"
        result['valid']     =   False
        result['result']    =   {"message":"Unauthorized access","data":{}}
        try:      
            from_user = request.Users_data
            friends_list = Friends.objects.filter( Q(to_user=from_user['id']), status='pending').values_list('from_user_id', flat=True).distinct()   
            # print("pending ",friends_list)    
            
            if not friends_list.exists():
                result['result']['message'] = "You don't have any pending friend requests!"
                return Response(result, status=status.HTTP_200_OK)    
            friends_data = Users.objects.filter(id__in=friends_list).values('id', 'name')
            paginated_data = self.paginate_queryset(friends_data, request, view=self)
            paginated_data = self.get_paginated_response(paginated_data).data
            result['status']              = "OK"
            result['valid']               = True
            result['result']['message']   = "Pending list fetched successfully!!"
            result['result']['next']      = paginated_data['next']
            result['result']['previous']  = paginated_data['previous']
            result['result']['count']     = paginated_data['count']
            result['result']['data']      = paginated_data['results']
            return Response(result, status=status.HTTP_200_OK)


        except Exception as e:
                result['result']['message'] = str(e)
                return Response(result, status=status.HTTP_401_UNAUTHORIZED)




class RejectedRequestsList(APIView,PageNumberPagination):
    @handle_auth_exceptions
    def get(self,request):
        result = {}
        result['status']    =   "NOK"
        result['valid']     =   False
        result['result']    =   {"message":"Unauthorized access","data":{}}
        try:      
            from_user = request.Users_data
            friends_list = Friends.objects.filter( Q(to_user=from_user['id']), status='rejected').values_list('from_user_id', flat=True).distinct()           
            if not friends_list.exists():
                result['result']['message'] = " No rejected friend requests!!"
                return Response(result, status=status.HTTP_200_OK)

            
            friends_data = Users.objects.filter(id__in=friends_list).values('id', 'name')       
            paginated_data = self.paginate_queryset(friends_data, request, view=self)
            paginated_data = self.get_paginated_response(paginated_data).data
            result['status']              = "OK"
            result['valid']               = True
            result['result']['message']   = "Rejected friend requests list fetched successfully!!"
            result['result']['next']      = paginated_data['next']
            result['result']['previous']  = paginated_data['previous']
            result['result']['count']     = paginated_data['count']
            result['result']['data']      = paginated_data['results']
            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
                result['result']['message'] = str(e)
                return Response(result, status=status.HTTP_401_UNAUTHORIZED)

