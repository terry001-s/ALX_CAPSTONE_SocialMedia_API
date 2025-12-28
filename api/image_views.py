from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
import cloudinary.uploader

class ImageUploadView(APIView):
    """Handle image uploads to Cloudinary"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Upload image to Cloudinary"""
        image_file = request.FILES.get('image')
        
        if not image_file:
            return Response(
                {"error": "No image file provided."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if image_file.content_type not in allowed_types:
            return Response(
                {"error": "Invalid file type. Allowed: JPG, PNG, GIF, WebP"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file size (max 5MB)
        if image_file.size > 5 * 1024 * 1024:
            return Response(
                {"error": "File too large. Max size is 5MB."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(
                image_file,
                folder="social_media/",
                transformation=[
                    {"width": 1200, "height": 1200, "crop": "limit"},
                    {"quality": "auto"},
                ]
            )
            
            return Response({
                "url": upload_result['secure_url'],
                "public_id": upload_result['public_id'],
                "format": upload_result['format'],
                "width": upload_result['width'],
                "height": upload_result['height']
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"error": f"Upload failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ImageDeleteView(APIView):
    """Delete image from Cloudinary"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, public_id):
        """Delete image by public_id"""
        try:
            result = cloudinary.uploader.destroy(public_id)
            
            if result.get('result') == 'ok':
                return Response(
                    {"message": "Image deleted successfully."},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"error": "Failed to delete image."},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {"error": f"Delete failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )