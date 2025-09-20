from django.shortcuts import render, redirect
from .models import Comment
from .forms import CommentForm

def leave_comment(request):
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("comments:all_comments")
    else:
        form = CommentForm()
    return render(request, "comments/leave_comment.html", {"form": form})

def all_comments(request):
    comments = Comment.objects.order_by("-created_at")
    return render(request, "comments/all_comments.html", {"comments": comments})
