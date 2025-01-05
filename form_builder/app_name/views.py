from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework import viewsets, permissions, status, parsers
from rest_framework.decorators import action
from rest_framework.response import Response as DRFResponse
from collections import Counter
from .models import Form, Question, Response, Answer
from .serializers import FormSerializer, QuestionSerializer, ResponseSerializer
import json
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse

# Create your views here.

class FormViewSet(viewsets.ModelViewSet):
    queryset = Form.objects.all()
    serializer_class = FormSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [parsers.JSONParser, parsers.FormParser, parsers.MultiPartParser]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        form = self.get_object()
        analytics_data = {}
        
        # Get responses in the last 24 hours
        last_24h = timezone.now() - timedelta(hours=24)
        recent_responses = Response.objects.filter(form=form, submitted_at__gte=last_24h)
        total_responses = Response.objects.filter(form=form).count()
        
        # Calculate response rate (responses in last 24h / total responses)
        response_rate = (recent_responses.count() / total_responses * 100) if total_responses > 0 else 0
        
        # Calculate average completion time
        completion_times = []
        for response in Response.objects.filter(form=form, completion_time__isnull=False):
            completion_times.append(response.completion_time)
        
        avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0

        # Get all responses with their answers
        responses_data = []
        for response in Response.objects.filter(form=form).order_by('-submitted_at'):
            response_data = {
                'submitted_at': response.submitted_at,
                'completion_time': response.completion_time,
                'answers': []
            }
            
            # Get answers for each question in the form
            for question in form.questions.all():
                answer = Answer.objects.filter(response=response, question=question).first()
                response_data['answers'].append({
                    'question_id': question.id,
                    'answer_text': answer.answer_text if answer else None
                })
            
            responses_data.append(response_data)
        
        # Add summary statistics
        analytics_data['summary'] = {
            'total_responses': total_responses,
            'response_rate': round(response_rate, 1),
            'avg_completion_time': avg_completion_time,
            'responses': responses_data
        }

        # Process each question
        for question in form.questions.all():
            answers = Answer.objects.filter(question=question)
            response_count = answers.count()
            
            question_data = {
                'type': question.question_type,
                'response_count': response_count
            }
            
            if question.question_type == 'text':
                # For text questions, show recent responses and word frequency
                recent_answers = answers.order_by('-response__submitted_at')[:10]
                question_data['recent_responses'] = [{
                    'date': answer.response.submitted_at,
                    'text': answer.answer_text
                } for answer in recent_answers]
                
                # Word frequency analysis
                words = []
                for answer in answers:
                    if answer.answer_text:
                        words.extend(answer.answer_text.lower().split())
                
                word_freq = Counter(words)
                question_data['word_distribution'] = word_freq.most_common(10)
                
            elif question.question_type == 'checkbox':
                # For checkbox questions, count individual option selections
                selections = []
                for answer in answers:
                    try:
                        if answer.answer_text:
                            selected = json.loads(answer.answer_text)
                            if isinstance(selected, list):
                                selections.extend(selected)
                    except json.JSONDecodeError:
                        continue
                
                selection_freq = Counter(selections)
                question_data['individual_distribution'] = selection_freq.most_common()
                
            else:  # dropdown
                # For dropdown questions, count each selection
                selection_freq = Counter(answer.answer_text for answer in answers if answer.answer_text)
                question_data['selection_distribution'] = selection_freq.most_common()
            
            analytics_data[question.id] = question_data
        
        return DRFResponse(analytics_data)

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ResponseViewSet(viewsets.ModelViewSet):
    queryset = Response.objects.all()
    serializer_class = ResponseSerializer
    permission_classes = [permissions.AllowAny]  # Allow anonymous submissions

    def create(self, request, *args, **kwargs):
        form_id = request.data.get('form')
        form = get_object_or_404(Form, id=form_id)
        
        print(f"Creating response for form {form_id}")  # Debug log
        print(f"Request data: {request.data}")  # Debug log
        
        # Validate required questions
        required_questions = form.questions.filter(required=True)
        submitted_answers = {answer['question']: answer for answer in request.data.get('answers', [])}
        
        for question in required_questions:
            if question.id not in submitted_answers:
                print(f"Missing required question: {question.id}")  # Debug log
                return DRFResponse(
                    {'error': f'Question {question.question_text} is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Create response and calculate completion time
        response = Response.objects.create(form=form)
        completion_time = (timezone.now() - response.start_time).total_seconds()
        response.completion_time = completion_time
        response.save()
        
        print(f"Created response {response.id} with completion time {completion_time}")  # Debug log
        
        # Create answers
        for answer_data in request.data.get('answers', []):
            question = get_object_or_404(Question, id=answer_data['question'])
            answer_text = answer_data['answer']
            
            # Convert list to JSON string for checkbox questions
            if question.question_type == 'checkbox' and isinstance(answer_text, list):
                answer_text = json.dumps(answer_text)
            
            answer = Answer.objects.create(
                response=response,
                question=question,
                answer_text=answer_text
            )
            print(f"Created answer for question {question.id}: {answer_text}")  # Debug log
        
        return DRFResponse(self.serializer_class(response).data, status=status.HTTP_201_CREATED)

# Template Views
def user_login(request):
    if request.user.is_authenticated:
        return redirect('list')
        
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'list')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'app_name/login.html')

def user_register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'app_name/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'app_name/register.html')
        
        user = User.objects.create_user(username=username, email=email, password=password1)
        login(request, user)
        messages.success(request, 'Registration successful!')
        return redirect('list')
    
    return render(request, 'app_name/register.html')

@login_required
def list(request):
    forms = Form.objects.filter(created_by=request.user)
    return render(request, 'app_name/list.html', {'forms': forms})

def fview(request, form_id):
    form = get_object_or_404(Form, id=form_id)
    # Only require login if viewing your own form
    if form.created_by == request.user:
        return render(request, 'app_name/fview.html', {'form': form})
    # For other users, redirect to form submission
    return redirect('fsubmit', form_id=form_id)

@login_required
def analytics(request, form_id):
    form = get_object_or_404(Form, id=form_id)
    if form.created_by != request.user:
        messages.error(request, "You don't have permission to view this form's analytics.")
        return redirect('list')
    return render(request, 'app_name/analytics.html', {'form': form})

def fsubmit(request, form_id):
    form = get_object_or_404(Form, id=form_id)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(f"Received data: {data}")  # Debug log
            
            # Create response object with start time
            start_time = data.get('start_time')
            end_time = data.get('end_time')
            
            try:
                start = timezone.datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                response = Response.objects.create(
                    form=form,
                    start_time=start
                )
                
                if end_time:
                    try:
                        end = timezone.datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                        completion_time = (end - start).total_seconds()
                        response.completion_time = completion_time
                        response.save()
                    except (ValueError, AttributeError) as e:
                        print(f"Error processing end time: {e}")  # Debug log
                        # Don't fail if end time is invalid, just skip setting completion time
                        pass
                
                # Process answers
                answers_data = data.get('answers', {})
                if not answers_data:
                    response.delete()  # Clean up if no answers
                    return JsonResponse({'error': 'No answers provided'}, status=400)
                
                # Keep track of required questions
                required_questions = {str(q.id): q for q in form.questions.filter(required=True)}
                answered_required = set()
                
                for field_name, answer_value in answers_data.items():
                    try:
                        # Extract question ID from field name (e.g., 'question_1' -> '1')
                        question_id = field_name.replace('question_', '')
                        question = Question.objects.get(id=question_id, form=form)
                        
                        # Skip empty answers for non-required questions
                        if not answer_value and not question.required:
                            continue
                            
                        # Handle different answer types
                        if isinstance(answer_value, list):  # Checkbox
                            if not answer_value and question.required:
                                response.delete()
                                return JsonResponse(
                                    {'error': f'Question "{question.question_text}" is required'},
                                    status=400
                                )
                            answer_text = json.dumps(answer_value)
                        else:  # Text or Dropdown
                            if not answer_value and question.required:
                                response.delete()
                                return JsonResponse(
                                    {'error': f'Question "{question.question_text}" is required'},
                                    status=400
                                )
                            answer_text = str(answer_value)
                        
                        # Create answer
                        Answer.objects.create(
                            response=response,
                            question=question,
                            answer_text=answer_text
                        )
                        
                        # Mark required question as answered
                        if question_id in required_questions:
                            answered_required.add(question_id)
                    
                    except Question.DoesNotExist:
                        response.delete()  # Clean up
                        return JsonResponse(
                            {'error': f'Invalid question ID: {question_id}'},
                            status=400
                        )
                    except Exception as e:
                        print(f"Error processing answer: {str(e)}")  # Debug log
                        response.delete()  # Clean up
                        return JsonResponse(
                            {'error': f'Error processing answer for question {question_id}: {str(e)}'},
                            status=400
                        )
                
                # Check if all required questions were answered
                missing_required = set(required_questions.keys()) - answered_required
                if missing_required:
                    response.delete()  # Clean up
                    missing_questions = [required_questions[qid].question_text for qid in missing_required]
                    return JsonResponse(
                        {'error': f'Required questions not answered: {", ".join(missing_questions)}'},
                        status=400
                    )
                
                return JsonResponse({'message': 'Form submitted successfully'}, status=201)
                
            except (ValueError, AttributeError) as e:
                print(f"Error processing start time: {e}")  # Debug log
                return JsonResponse({'error': 'Invalid start time format'}, status=400)
                
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")  # Debug log
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            print(f"Unexpected error: {str(e)}")  # Debug log
            return JsonResponse({'error': str(e)}, status=400)
    
    return render(request, 'app_name/fsubmit.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')
