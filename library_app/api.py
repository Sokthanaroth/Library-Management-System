from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Book, Member, BorrowRecord
from .serializers import BookSerializer, MemberSerializer, BorrowRecordSerializer

class IsLibrarian(permissions.BasePermission):
    """
    Custom permission to only allow librarians to access the view.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated, IsLibrarian]
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def public_list(self, request):
        """
        Public endpoint for book listing (no authentication required)
        """
        books = Book.objects.all()
        serializer = self.get_serializer(books, many=True)
        return Response(serializer.data)

class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = [permissions.IsAuthenticated, IsLibrarian]

class BorrowRecordViewSet(viewsets.ModelViewSet):
    queryset = BorrowRecord.objects.all()
    serializer_class = BorrowRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsLibrarian]
    
    @action(detail=False, methods=['get'])
    def my_borrowings(self, request):
        """
        Get current user's borrow records
        """
        if hasattr(request.user, 'member'):
            borrow_records = BorrowRecord.objects.filter(member=request.user.member)
            serializer = self.get_serializer(borrow_records, many=True)
            return Response(serializer.data)
        return Response([], status=status.HTTP_200_OK)
