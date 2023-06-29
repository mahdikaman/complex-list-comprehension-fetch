from flask import Flask, render_template ,jsonify
import requests
import json
from datetime import datetime
import datetime
import calendar 
from flask_cors import CORS

app = Flask(__name__, static_url_path='/static')
CORS(app)

headers = {
        "Content-Type": "application/json",
        "Accept": "application/hal+json",
        "x-api-key": ""
}
url = ""


def get_limeobjects(headers=headers, url=url):
    response = requests.get(url=url,
                            headers=headers,
                            data=None,
                            verify=False)

    json_data = json.loads(response.text)
    limeobjects = json_data.get("_embedded").get("limeobjects")

    nextpage = json_data.get("_links").get("next")
    while nextpage is not None:
        url = nextpage["href"]
        response = requests.get(url=url,
                                headers=headers,
                                data=None,
                                verify=False)

        json_data = json.loads(response.text)
        limeobjects += json_data.get("_embedded").get("limeobjects")
        nextpage = json_data.get("_links").get("next")
    
    return limeobjects

def get_companies(headers,url):
    response = requests.get(url=url,
                            headers=headers,
                            data=None,
                            verify=False)

    json_data = json.loads(response.text)
    limeobjects = json_data.get("_embedded").get("limeobjects")

    nextpage = json_data.get("_links").get("next")
    while nextpage is not None:
        url = nextpage["href"]
        response = requests.get(url=url,
                                headers=headers,
                                data=None,
                                verify=False)

        json_data = json.loads(response.text)
        limeobjects += json_data.get("_embedded").get("limeobjects")
        nextpage = json_data.get("_links").get("next")
    
    return limeobjects

def all_customer_companies():
    deals = get_limeobjects()
    
    current_year = datetime.datetime.now().year
    last_year = current_year - 1 
    #filters deals that that has closeddate and the year of closeddate is last year and the dealstatus is agreed
    won_deals_last_year = [deal for deal in deals if  deal.get("closeddate") 
    and datetime.datetime.strptime(deal["closeddate"].split("T")[0], "%Y-%m-%d").year == last_year and deal.get("dealstatus",{}).get("key")=="agreement"]
    #Get the name of the companies that has won deal last year
    company_names = [deal.get("_embedded" , {}).get("relation_company",{}).get("name") or "no company name" for deal in won_deals_last_year]
    none_repeat_company_customers = list(set(company_names))
    
    
    return none_repeat_company_customers

def all_customer_companies_before_lastyear():
    deals = get_limeobjects()
    
    current_year = datetime.datetime.now().year
    # get the deals that has closeddate before last year and has a value on the deal
    inactive = [deal for deal in deals if deal.get("value") != 0 and deal.get("closeddate") and (current_year - datetime.datetime.strptime(deal["closeddate"].split("T")[0], "%Y-%m-%d").year) > 1]
    # gets the company name of the mentioned deals above
    company_names = [deal.get("_embedded" , {}).get("relation_company",{}).get("name") or "no company name" for deal in inactive]
    # removes duplicate names
    none_repeat_company = list(set(company_names))

    return none_repeat_company

@app.route('/')
def index():
    return "welcome"

@app.route('/average_deals_last_year')
def average_won_deals_last_year():
    deals = get_limeobjects()

    current_year = datetime.datetime.now().year
    last_year = current_year - 1 

    #filters deals that that has closeddate and the year of closeddate is last year and the dealstatus is agreed
    won_deals_last_year = [deal for deal in deals if  deal.get("closeddate") 
    and datetime.datetime.strptime(deal["closeddate"].split("T")[0], "%Y-%m-%d").year == last_year and deal.get("dealstatus",{}).get("key")=="agreement"]
    # gets the value of won deals last year
    values_won_deal = [deal.get("value") for deal in won_deals_last_year]
    summed_values_won_deal = sum(values_won_deal)
    average_values_won_deal = summed_values_won_deal / len(values_won_deal)
    formatted_average_won_deal = '${:,.2f}'.format(average_values_won_deal)
    response_data = json.dumps(formatted_average_won_deal)
    
    return response_data

@app.route('/deals_per_month_last_year')
def won_deals_per_month_last_year():
    deals = get_limeobjects()
    
    current_year = datetime.datetime.now().year
    last_year = current_year - 1 
    
    #filters deals that that has closeddate and the year of closeddate is last year and the dealstatus is agreed
    won_deals_last_year = [deal for deal in deals if  deal.get("closeddate") 
    and datetime.datetime.strptime(deal["closeddate"].split("T")[0], "%Y-%m-%d").year == last_year and deal.get("dealstatus",{}).get("key")=="agreement"]
    closed_dates = [deal.get("closeddate") for deal in won_deals_last_year]

    monthtly_dates = {}
    # loops and if the month deal exists it sums the number of deals on it
    for date_str in closed_dates:
        date = datetime.datetime.fromisoformat(date_str.split("T")[0])
        month = date.strftime("%B")

        if month not in monthtly_dates:
            monthtly_dates[month]=[]
        monthtly_dates[month].append(date_str)
    
    months = list(calendar.month_name[1:])
    monthly_dates_number = {month: len(monthtly_dates.get(month,[])) for month in months}
    response_data = json.dumps(monthly_dates_number)
    
    return response_data

@app.route('/won_deals_per_customer')
def won_deals_per_customer_last_year():
    deals = get_limeobjects()
    
    current_year = datetime.datetime.now().year
    last_year = current_year - 1 
    
    #filters deals that that has closeddate and the year of closeddate is last year and the dealstatus is agreed
    won_deals_last_year = [deal for deal in deals if  deal.get("closeddate") 
    and datetime.datetime.strptime(deal["closeddate"].split("T")[0], "%Y-%m-%d").year == last_year and deal.get("dealstatus",{}).get("key")=="agreement"]
    
    company_names_won_deal = [(deal.get("_embedded" , {}).get("relation_company",{}).get("name") , deal.get("value")) for deal in won_deals_last_year]
    
    company_values = {}
    # loops and and sums the value for each company that has done won deal
    for company,value in company_names_won_deal:
        if company in company_values:
            company_values[company] += value
        else:
            company_values[company]= value
    
    sum_repeating_companies = {company: "${:,.2f}".format(value) for company, value in company_values.items() if value >= 0}
    response_data = json.dumps(sum_repeating_companies)
    
    return response_data

@app.route('/customer_companies')
def find_customer_companies():
    deals = get_limeobjects()
    customer_list = all_customer_companies()
    response_data = json.dumps(customer_list)
    
    return response_data

@app.route('/inactive_companies')
def find_inactive_companies():
    deals = get_limeobjects()
    before_lastyear_customers = all_customer_companies_before_lastyear()
    customer_list = all_customer_companies()

    remove_duplicate_name_in_customerlist = [name for name in before_lastyear_customers if name not in customer_list]
    response_data = json.dumps(remove_duplicate_name_in_customerlist)
    
    return response_data

@app.route('/prospect_companies')
def find_prospect_companies():
    companies = get_companies(headers,"https://api-test.lime-crm.com/api-test/api/v1/limeobject/company/?_limit=50")
    # filters all companies from notinterested 
    filtered_notintressed_allcompanies = [company for company in companies if company.get("buyingstatus",{}).get("key") != "notinterested"]
    names_of_filtered_notintressed_allcompanies = [company.get("name") for company in filtered_notintressed_allcompanies]
    # gets the list of companies that are customers
    customer_list = all_customer_companies()
    # gets the list of companies that are inactive
    customers_before_last_year = all_customer_companies_before_lastyear()
    
    # sums them in list and remove duplicate names
    all_company_names_bought = customer_list + customers_before_last_year
    none_repeat_all_names = list(set(all_company_names_bought))
    # filters all companies except notinterested companies and checks that the company name is not in the list of summed customers and inactive companies
    prospect = [item for item in names_of_filtered_notintressed_allcompanies if item not in none_repeat_all_names]
    response_data = json.dumps(prospect)
    
    return response_data


@app.route('/deals_without_company_info')
def find_deals_without_company():
    deals = get_limeobjects(headers)
    # gets the deal that has no company information
    none_company_names = [deal for deal in deals if not deal.get("_embedded")]
    get_id= [deal.get("_id") for deal in none_company_names]
    response_data = json.dumps(get_id)
    
    return response_data


if __name__ == '__main__':
    app.secret_key = 'somethingsecret'
    app.run(debug=True)