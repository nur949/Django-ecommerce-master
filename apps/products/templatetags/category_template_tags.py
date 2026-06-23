from django import template
from django.utils.safestring import mark_safe

from apps.products.models import Category

register = template.Library()

def get_base_categories():
    return Category.objects.filter(is_active=True).exclude(
        title__iexact="Season's Essentials"
    ).exclude(
        slug__iexact="seasons-essentials"
    ).exclude(
        title__iexact="Training's Essentials"
    ).exclude(
        slug__iexact="trainings-essentials"
    )

@register.simple_tag
def categories():
    items = get_base_categories().order_by('title')
    items_li = ""
    for i in items:
        items_li += """<li><a href="/category/{}">{}</a></li>""".format(i.slug, i.title)
    return mark_safe(items_li)

@register.simple_tag
def categories_mobile():
    items = get_base_categories().order_by('title')
    items_li = ""
    for i in items:
        items_li += """<li class="item-menu-mobile"><a href="/category/{}">{}</a></li>""".format(i.slug, i.title)
    return mark_safe(items_li)

@register.simple_tag
def categories_li_a():
    items = get_base_categories().order_by('title')
    items_li_a = ""
    for i in items:
        items_li_a += """<li class="p-t-4"><a href="/category/{}" class="s-text13">{}</a></li>""".format(i.slug,
                                                                                                         i.title)
    return mark_safe(items_li_a)

@register.simple_tag
def get_categories():
    return get_base_categories().order_by('title')

@register.simple_tag
def categories_div():
    """
    section banner
    :return:
    """
    items = get_base_categories().order_by('title')
    items_div = ""
    item_div_list = ""
    for i, j in enumerate(items):
        if not i % 2:
            items_div += """<div class="block1 hov-img-zoom pos-relative m-b-30"><img src="/media/{}" alt="IMG-BENNER"><div class="block1-wrapbtn w-size2"><a href="/category/{}" class="flex-c-m size2 m-text2 bg3 hov1 trans-0-4">{}</a></div></div>""".format(
                j.image, j.slug, j.title)
        else:
            items_div_ = """<div class="block1 hov-img-zoom pos-relative m-b-30"><img src="/media/{}" alt="IMG-BENNER"><div class="block1-wrapbtn w-size2"><a href="/category/{}" class="flex-c-m size2 m-text2 bg3 hov1 trans-0-4">{}</a></div></div>""".format(
                j.image, j.slug, j.title)
            item_div_list += """<div class="col-sm-10 col-md-8 col-lg-4 m-l-r-auto">""" + items_div + items_div_ + """</div>"""
            items_div = ""

    return mark_safe(item_div_list)

@register.simple_tag
def categories_circles():
    items = get_base_categories().order_by('title')
    html = '<div class="circular-categories-container">'
    for i in items:
        img_url = f"/media/{i.image}" if i.image else "/static/images/placeholder.jpg"
        html += f"""
        <div class="category-circle-item text-center">
            <a href="/category/{i.slug}" class="d-inline-block category-circle-link">
                <div class="category-circle-wrapper">
                    <img src="{img_url}" alt="{i.title}" class="category-circle-img">
                </div>
                <h5 class="category-circle-title">{i.title}</h5>
            </a>
        </div>
        """
    html += '</div>'
    return mark_safe(html)
