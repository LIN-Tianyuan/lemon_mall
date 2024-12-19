# Product

## 1. Product database table design
### 1.1 SPU and SKU

For merchandise in e-commerce, there are two important concepts: the SPU and the SKU.

#### 1.1.1 Introduction to SPU

**SPU = Standard Product Unit**
 - SPU is the smallest unit of commodity information aggregation, is a set of standardized information that can be taken, easy to retrieve the collection, the collection describes the characteristics of a product.

 - In common parlance, goods with the same attribute values and characteristics can be categorized into one type of SPU.

 - Example:
   - iPhone X is an SPU, independent of merchant, color, style, specification, package, etc.
      ![img_docs](img_docs/01spu.png)

#### 1.1.2 Introduction to SKU

**SKU = Stock Keeping Unit**
 - SKU, the unit of measurement of inventory in and out, can be in pieces, boxes, etc., is the smallest physically indivisible unit of inventory.
 - In layman's terms, a SKU is an item, each with a SKU, which makes it easy for e-commerce brands to identify the item.
 - Example:
   - iPhone X Full Netflix Black 256G is a SKU that indicates specific specifications, colors, and other information.
     ![img_docs](img_docs/02sku.png)

### 1.2 Home Ads Database Table Analysis
#### 1.2.1 Home Ads Database Table Analysis
![img_docs](img_docs/03adv.png)

#### 1.2.2 Define the home page ad model class
[Details](../lemon_mall/lemon_mall/apps/contents/models.py)
```python
class ContentCategory(BaseModel):
    ...


class Content(BaseModel):
    ...
```
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

### 1.3 Commodity information database table analysis
#### 1.3.1 Commodity information database table analysis
![img_docs](img_docs/04pro.png)

#### 1.3.2 Define the commodity information model class
```bash
cd lemon_mall
cd apps
python3 ../../manage.py startapp goods
```
[Details](../lemon_mall/lemon_mall/apps/goods/models.py)
```python
from lemon_mall.utils.models import BaseModel


class GoodsCategory(BaseModel):
    ...


class GoodsChannelGroup(BaseModel):
    ...


class GoodsChannel(BaseModel):
    ...


class Brand(BaseModel):
    ...


class SPU(BaseModel):
    ...


class SKU(BaseModel):
    ...


class SKUImage(BaseModel):
    ...


class SPUSpecification(BaseModel):
    ...


class SpecificationOption(BaseModel):
    ...


class SKUSpecification(BaseModel):
    ...
```
```bash
INSTALLED_APPS = [
    ...
    'goods',  # Goods
]
```
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

## 2. Preparation of commodity data
 - With the database tables in place, we now need to prepare the product information data and product image data for querying and display.
 - Commodity information data: such as item numbers are of string type and can be stored directly in the MySQL database.
 - Product Image Data: MySQL usually stores the address string information of the image.
   - So the image data needs to be stored physically in some other way.
   ![img_docs](img_docs/05image.png)
 - Image physical storage thinking:
   - Need to provide mechanisms for image uploads and downloads.
   - Need to solve the problem of image backup and expansion.
   - Need to solve the problem of image renaming and so on.
 - Physical storage solution for images:
   - FastDFS