# pylint: disable=unbalanced-tuple-unpacking
from rest_framework import generics
from rest_framework.response import Response

from oscar.core.loading import get_class , get_model

from oscarapi.utils.categories import find_from_full_slug
from oscarapi.utils.loading import get_api_classes , get_api_class

Selector = get_class("partner.strategy" , "Selector")
(
    CategorySerializer ,
    ProductLinkSerializer ,
    ProductSerializer ,
    ProductStockRecordSerializer ,
    AvailabilitySerializer ,
    ProductAttributeSerializer ,
    ProductAttributeValueSerializer ,
    ProductImageSerializer ,
) = get_api_classes(
    "serializers.product" ,
    [
        "CategorySerializer" ,
        "ProductLinkSerializer" ,
        "ProductSerializer" ,
        "ProductStockRecordSerializer" ,
        "AvailabilitySerializer" ,
        "ProductAttributeSerializer" ,
        "ProductAttributeValueSerializer" ,
        "ProductImageSerializer"
    ] ,
)

PriceSerializer = get_api_class("serializers.checkout" , "PriceSerializer")

__all__ = ("ProductList" , "ProductDetail" , "ProductPrice" , "ProductAvailability")

Product = get_model("catalogue" , "Product")
Category = get_model("catalogue" , "Category")
StockRecord = get_model("partner" , "StockRecord")
ProductAttribute = get_model("catalogue" , "ProductAttribute")
ProductAttributeValue = get_model("catalogue" , "ProductAttributeValue")
ProductImage = get_model("catalogue" , "ProductImage")


class ProductList(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductLinkSerializer

    def get_queryset(self):
        """
        Allow filtering on structure so standalone and parent products can
        be selected separately, eg::

            http://127.0.0.1:8000/api/products/?structure=standalone

        or::

            http://127.0.0.1:8000/api/products/?structure=parent
        """
        qs = super(ProductList , self).get_queryset()
        structure = self.request.query_params.get("structure")
        if structure is not None:
            return qs.filter(structure = structure)

        return qs


class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductPrice(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = PriceSerializer

    def get(
            self , request , pk = None , *args , **kwargs
    ):  # pylint: disable=redefined-builtin,arguments-differ
        product = self.get_object()
        strategy = Selector().strategy(request = request , user = request.user)
        ser = PriceSerializer(
            strategy.fetch_for_product(product).price , context = {"request": request}
        )
        return Response(ser.data)


class ProductStockRecords(generics.ListAPIView):
    serializer_class = ProductStockRecordSerializer
    queryset = StockRecord.objects.all()

    def get_queryset(self):
        product_pk = self.kwargs.get("pk")
        return super().get_queryset().filter(product_id = product_pk)


class ProductStockRecordDetail(generics.RetrieveAPIView):
    serializer_class = ProductStockRecordSerializer
    queryset = StockRecord.objects.all()


class ProductAvailability(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = AvailabilitySerializer

    def get(
            self , request , pk = None , *args , **kwargs
    ):  # pylint: disable=redefined-builtin,arguments-differ
        product = self.get_object()
        strategy = Selector().strategy(request = request , user = request.user)
        ser = AvailabilitySerializer(
            strategy.fetch_for_product(product).availability ,
            context = {"request": request} ,
        )
        return Response(ser.data)


class CategoryList(generics.ListAPIView):
    queryset = Category.get_root_nodes()
    serializer_class = CategorySerializer

    def get_queryset(self):
        breadcrumb_path = self.kwargs.get("breadcrumbs" , None)
        if breadcrumb_path is None:
            return super(CategoryList , self).get_queryset()

        return find_from_full_slug(breadcrumb_path , separator = "/").get_children()


class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductAttributeList(generics.ListCreateAPIView):
    queryset = ProductAttribute.objects.all()
    serializer_class = ProductAttributeSerializer


class ProductAttributeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductAttribute.objects.all()
    serializer_class = ProductAttributeSerializer


class ProductAttributeValueList(generics.ListCreateAPIView):
    queryset = ProductAttributeValue.objects.all()
    serializer_class = ProductAttributeValueSerializer


class ProductAttributeValueDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductAttributeValue.objects.all()
    serializer_class = ProductAttributeValueSerializer


class ProductImageList(generics.ListCreateAPIView):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer


class ProductImageDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
