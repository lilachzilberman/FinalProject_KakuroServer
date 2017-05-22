package colman66.kakuro.server;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.JsonNodeFactory;

import org.chocosolver.solver.*;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.exception.ContradictionException;
import org.chocosolver.solver.variables.IntVar;

import java.util.Vector;
public final class KakuroSolver {
    private ArrayNode board;
    private JsonNode solved;

    private static int numOfCols(ArrayNode board) {
        if (board.size() == 0) {
            return 0;
        }
        int cols = 0;
        for (int i = 0; i < board.size(); ++i) {
            ArrayNode row = (ArrayNode) board.get(i);
            if (i == 0) {
                cols = row.size();
            } else {
                assert( cols == row.size() );
            }
        }
        return cols;
    }

    private static int numOfRows(ArrayNode board) {
        return board.size();
    }

    public KakuroSolver(ArrayNode board) {
        this.board = board;

        this.solved = board.deepCopy();

        Model model = new Model("Kakuro board");
        IntVar[][] k = model.intVarMatrix("k", numOfRows(board), numOfCols(board), 1, 9);
        for (int i = 0; i < board.size(); ++i) {
            ArrayNode row = (ArrayNode) board.get(i);
            for (int j = 0; j < row.size(); ++j) {
                JsonNode cell = row.get(j);
                if (!cell.isObject()) {
                    continue;
                }
                int sumRight = cell.has("right") ? cell.get("right").asInt(0) : 0;
                if (sumRight > 0) {
                    Vector<IntVar> elems = new Vector<IntVar>();
                    IntVar[] elemArray = new IntVar[0];
                    for (int jf = j + 1; jf < row.size(); ++jf) {
                        JsonNode cellf = row.get(jf);
                        if (cellf.isObject() || cellf.isTextual()) break;
                        elems.add(k[i][jf]);
                        if (cellf.isNumber()) {
                            try {
                                k[i][jf].updateBounds(cellf.asInt(), cellf.asInt(), Cause.Null);
                            } catch (ContradictionException e) {

                            }
                        }
                    }
                    elemArray = elems.toArray(elemArray);
                    if (elemArray.length > 0) {
                        model.sum(elemArray.clone(), "=", sumRight).post();
                        model.allDifferent(elemArray.clone()).post();
                    }
                }
                int sumDown = cell.has("down") ? cell.get("down").asInt(0) : 0;
                if (sumDown > 0) {
                    Vector<IntVar> elems = new Vector<IntVar>();
                    IntVar[] elemArray = new IntVar[0];
                    
                    for (int il = i + 1; il < numOfRows(board); ++il) {
                        JsonNode cellf = ((ArrayNode) board.get(il)).get(j);
                        if (cellf.isObject() || cellf.isTextual()) break;
                        elems.add(k[il][j]);
                        if (cellf.isNumber()) {
                            try {
                                k[il][j].updateBounds(cellf.asInt(), cellf.asInt(), Cause.Null);
                            } catch (ContradictionException e) {

                            }
                        }
                    }
                    elemArray = elems.toArray(elemArray);
                    if (elemArray.length > 0) {
                        model.sum(elemArray.clone(), "=", sumDown).post();
                        model.allDifferent(elemArray.clone()).post();
                    }
                }
            }
        }
        Solver solver = model.getSolver();
        solver.setSearch(Search.defaultSearch(model));
        if (!solver.solve()) {
            this.solved = JsonNodeFactory.instance.textNode("NOT SOLVED");
            return;
        }
        for (int i = 0; i < solved.size(); ++i) {
            ArrayNode row = (ArrayNode) solved.get(i);
            for (int j = 0; j < row.size(); ++j) {
                JsonNode cell = row.get(j);
                if (!cell.isNull()) {
                    continue;
                }
                row.set(j, JsonNodeFactory.instance.numberNode(k[i][j].getValue()));
            }
        }
    }
    
    public JsonNode getSolvedJson() {
        return this.solved;
    }

    public JsonNode getBoardJson() {
        return this.board;
    }
}