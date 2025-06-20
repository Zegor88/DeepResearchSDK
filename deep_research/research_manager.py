from agents import trace, Runner, gen_trace_id
from initial_research_agent import initial_research_agent
from planner_agent import planner_agent, WebSearchItem, WebSearchPlan
from deep_researcher_agent import deep_search_agent
from writer_agent import writer_agent
import asyncio

class ResearchManager:
    async def run(self, query: str):
        """ Run the deep research process, yielding the status updates and the final report"""
        trace_id = gen_trace_id()
        with trace("DeepResearch"):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}")
            yield f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}"
            print("Starting research...")
            yield f"Performing initial research..."
            initial_search = await self.initial_research(query)
            yield f"Planning searches..."
            search_plan = await self.plan_searches(initial_search)
            yield f"Performing deep research..."
            search_results = await self.perform_searches(search_plan)
            yield f"Writing report..."
            report = await self.write_report(query, search_results)
            yield f"Report is ready"
            yield report.markdown_report

    async def initial_research(self, query: str):
        """ Use the initial_research_agent to perform the initial research to get the draft of the report """
        print("Initial researches...")
        result = await Runner.run(initial_research_agent, f"Query: {query}")
        return result.final_output

    async def plan_searches(self, query: str):
        """ Use the planner_agent to plan which searches to run for the query """
        print("Planning searches...")
        result = await Runner.run(planner_agent, f"Query: {query}")
        print(f"Will perform {len(result.final_output.searches)} searches")
        return result.final_output

    async def search(self, item: WebSearchItem):
        """ Use the search agent to run a web search for each item in the search plan """
        input = f"Search term: {item.query}\nReason for searching: {item.reason}"
        result = await Runner.run(deep_search_agent, input)
        return result.final_output

    async def perform_searches(self, search_plan: WebSearchPlan):
        """ Call search() for each item in the search plan """
        print("Searching...")
        tasks = [asyncio.create_task(self.search(item)) for item in search_plan.searches]
        results = await asyncio.gather(*tasks)
        print("Finished searching")
        return results
    
    async def write_report(self, query: str, search_results: list[str]):
        """ Use the writer agent to write a report based on the search results"""
        print("Thinking about report...")
        input = f"Original query: {query}\nSummarized search results: {search_results}"
        result = await Runner.run(writer_agent, input)
        print("Finished writing report")
        return result.final_output