# Lemon Mall

## [1. Project preparation](./docs/01_project/README.md)
### Pivot
 - Introduction to the project
 - Project creation and configuration
```bash
# Create Project
python3 -m venv lemonmall-env
source lemonmall-env/bin/activate
pip3 install django

django-admin startproject lemon_mall
python manage.py runserver
```
```bash
# Configure mysql database
create database lemonmall charset=utf8; # Create a new MySQL database
create user alex identified by '123456abcdefg'; # Create a new MySQL user
grant all on lemonmall.* to 'alex'@'%'; # Authorizing alex users to access the lemon_mall database
flush privileges; # Refresh privileges after authorization ends
```
## [2. User Registration](./docs/02_user_registration/README.md)
### Pivot
- Show user registration page
## [6. Product](./docs/06_product/README.md)
### Pivot
- Commodity database table design
- Preparation of commodity data
- Home Ads
- Home List Page
### Notice
 - Paging
```python
# Paging
from django.core.paginator import Paginator, EmptyPage
# Creating a Paginator
# Paginator('Data to be paged', 'Number of records per page')
paginator = Paginator(skus, 5)  # Pagination of skus with 5 records per page
try:
   # Get the page the user is currently looking at(Core data)
   page_skus = paginator.page(page_num)    # Gets the five records in the page_nums page.
except EmptyPage:
   return http.HttpResponseNotFound('Empty Page')

# Get Total Pages: The front-end paging plugin requires the use
total_page = paginator.num_pages
```
```html
<div class="r_wrap fr clearfix">
    ......
    <div class="pagenation">
        <div id="pagination" class="page"></div>
    </div>
</div>

<link rel="stylesheet" type="text/css" href="{{ static('css/jquery.pagination.css') }}">

<script type="text/javascript" src="{{ static('js/jquery.pagination.min.js') }}"></script>

<script type="text/javascript">
    $(function () {
        $('#pagination').pagination({
            currentPage: {{ page_num }},
            totalPage: {{ total_page }},
            callback:function (current) {
                {#location.href = '/list/115/1/?sort=default';#}
                location.href = '/list/{{ category.id }}/' + current + '/?sort={{ sort }}';
            }
        })
    });
</script>
```
 - ElasticSearch



## License

[MIT](https://choosealicense.com/licenses/mit/)