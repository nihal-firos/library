from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.utils import timezone

from .models import Book, BorrowRecord
from .forms import SignUpForm, BookForm

def is_staff_user(user):
    return user.is_staff

def register_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created — you are now logged in.')
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'library_app/register.html', {'form': form})

def home_view(request):
    q = request.GET.get('q', '')
    books = Book.objects.all()
    if q:
        books = books.filter(
            Q(title__icontains=q) | Q(author__icontains=q) | Q(genre__icontains=q)
        )
    return render(request, 'library_app/home.html', {'books': books, 'q': q})

def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)

    user_has_borrowed = False
    if request.user.is_authenticated:
        user_has_borrowed = BorrowRecord.objects.filter(
            book=book, user=request.user, returned_at__isnull=True
        ).exists()

    active_record = BorrowRecord.objects.filter(book=book, returned_at__isnull=True).first()

    return render(request, 'library_app/book_detail.html', {
        'book': book,
        'user_has_borrowed': user_has_borrowed,
        'active_record': active_record,
    })

@login_required
def borrow_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if book.is_borrowed:
        messages.error(request, 'Sorry, this book is already borrowed.')
        return redirect('book_detail', pk=pk)

    if request.method == 'POST':
        book.is_borrowed = True
        book.borrowed_by = request.user
        book.save()
        BorrowRecord.objects.create(user=request.user, book=book)
        messages.success(request, f'You have borrowed \"{book.title}\". Enjoy!')
    return redirect('book_detail', pk=pk)

@login_required
def return_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    record = BorrowRecord.objects.filter(book=book, user=request.user, returned_at__isnull=True).first()
    if not record:
        messages.error(request, "You don't have this book borrowed.")
        return redirect('book_detail', pk=pk)

    if request.method == 'POST':
        record.returned_at = timezone.now()
        record.save()
        book.is_borrowed = False
        book.borrowed_by = None
        book.save()

        record = BorrowRecord.objects.filter(user=request.user, book=book, returned_at__isnull=True).first()
        if record:
            record.returned_at = timezone.now()
            record.save()

        messages.success(request, f'You have returned \"{book.title}\". Thanks!')
    return redirect('book_detail', pk=pk)

@login_required
@user_passes_test(is_staff_user)
def add_book_view(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book added successfully.')
            return redirect('home')
    else:
        form = BookForm()
    return render(request, 'library_app/add_book.html', {'form': form})

@login_required
def dashboard(request):
    borrowed = BorrowRecord.objects.filter(user=request.user, returned_at__isnull=True)
    return render(request, 'library_app/dashboard.html', {'borrowed': borrowed})
