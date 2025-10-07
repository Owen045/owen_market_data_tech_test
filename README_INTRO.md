## Technical Assessment: Commercial Real Estate Analytics API
### Overview

Build a RESTful API using Django rest framework OR FastAPI that provides analytical insights for commercial real estate properties by comparing individual asset performance against market benchmarks. 

I've provided two files: ```market_data.json``` and ```property_data.json``` which should have all the information required to build out the API. 

You are welcome to use AI to help you write code, as long as it is used in a controlled manner and you can explain reasoning behind decisions. 

### Business Context

As a CRE professional, you need to assess how your properties are performing relative to market averages across geographic regions. This API will power dashboards that help investment teams make data-driven decisions about their real estate assets.

### Timeframe guidelines

We recommend no more than 2 hours spent on this task:
- 90 minutes on development of the API and service logic
- 30 minutes writing a brief performance & scalability analysis (details to cover below)

## Core API (90 minutes)

**Note: The following endpoints are guidelines to build around and are not required in the exact format.**

1. Market Overview

```/api/markets/{marketId}```

Retrieve the latest market data.
Bonus considerations: specified date range (i.e. YTD), trend analysis, specified metrics

Expected response: Not defined, suggest the best format for the data.

2. Single Asset Performance Analysis

```/api/properties/{propertyId}/market-performance```

Compare an individual property against its latest local market benchmarks.
Bonus considerations: Historic market analysis.

Expected Response: Performance metrics with clear variance indicators and market context

3. Multi-Asset market performance

```/api/markets/{market}/properties```

Get the performance of all the properties in a market.
Bonus considerations: Sort, filter, paginate, historic comparison.


### Evaluation Criteria

- API Design & Implementation: RESTful principles, clean endpoints, proper error handling
- Analytical Logic: Meaningful calculations, appropriate handling of missing data, business-relevant insights
- Code Quality: Structure, readability, basic validation
- Analysis: Understanding of the domain needs and ideas for enhancement

### Performance & Scalability Analysis (30 minutes)

Provide a written analysis using SOME of the following for consideration:

Performance Considerations
- Identify potential bottlenecks in your current implementation
- Discuss computational complexity of your analytical calculations
- Consider memory usage with larger datasets
- Analyze response time implications

Scalability Enhancements

- How would you handle 1000+ properties across 50+ markets?
- Database design considerations for production scale (in brief)
- Caching strategies for frequently accessed calculations
- API rate limiting and pagination needs

Future Enhancements
- Additional analytical capabilities you would add
- Advanced analytics
- Integration possibilities with external data sources
- Monitoring and observability considerations
