from django.template.defaulttags import register

@register.filter
def show_page(i_page, current_page):
	if abs(i_page - current_page)<=3:
		return True
	else:
		return False