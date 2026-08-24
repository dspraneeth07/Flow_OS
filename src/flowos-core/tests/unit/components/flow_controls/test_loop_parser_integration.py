"""Integration test for Loop + Parser bug fix.

This test reproduces the bug reported where a Parser component inside a Loop
was receiving None during the build phase, causing:
"Unsupported input type: <class 'NoneType'>. Expected DataFrame or Data."
"""

import pytest
from flowos_core.components.flow_controls.loop import LoopComponent
from flowos_core.components.input_output import ChatOutput
from flowos_core.components.processing.parser import ParserComponent
from flowos_core.graph import Graph
from flowos_core.schema.data import Data
from flowos_core.schema.dataframe import DataFrame


class TestLoopParserIntegration:
    """Test that Parser component works correctly inside a Loop."""

    @pytest.mark.asyncio
    async def test_parser_receives_loop_item_during_build(self):
        """Test that Parser gets loop item before validation during build.

        This reproduces the bug where Parser would get None during prepare()
        and fail validation.
        """
        # Create loop with test data
        loop = LoopComponent(_id="loop")
        test_data = [
            Data(text="First item"),
            Data(text="Second item"),
            Data(text="Third item"),
        ]
        loop.set(data=DataFrame(test_data))

        # Create parser that receives loop items
        parser = ParserComponent(_id="parser")
        parser.set(
            input_data=loop.item_output,
            pattern="Item: {text}",
            mode="Parser",
        )

        # Create output
        chat_output = ChatOutput(_id="output")
        chat_output.set(input_value=parser.parsed_text)

        # Connect parser output back to loop done (completes the loop body)
        loop.set(item=chat_output.message)

        # Build graph - this should NOT fail with "Unsupported input type: NoneType"
        graph = Graph(loop, chat_output)

        # Execute the loop - parser should receive each item correctly
        # The key test is that this DOESN'T raise "Unsupported input type: NoneType"
        results = [result async for result in graph.async_start()]

        # Verify execution completed without errors
        assert len(results) > 0

        # Check that we got valid results (not all errors)
        valid_results = [r for r in results if hasattr(r, "valid") and r.valid]
        assert len(valid_results) > 0
