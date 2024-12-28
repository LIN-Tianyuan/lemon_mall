def get_breadcrumb(category):
    """
    Get Breadcrumb Navigation
    :param category: first, second, third
    :return: first: return first level; second: return first level + second level; third: return first level + second level + third level
    """
    breadcrumb = {
        'cat1': '',
        'cat2': '',
        'cat3': ''
    }
    if category.parent == None: # First level
        breadcrumb['cat1'] = category
    elif category.subs.count() == 0:    # Third level
        cat2 = category.parent
        breadcrumb['cat1'] = cat2.parent
        breadcrumb['cat2'] = cat2
        breadcrumb['cat3'] = category
    else:   # Second level
        breadcrumb['cat1'] = category.parent
        breadcrumb['cat2'] = category

    return breadcrumb
