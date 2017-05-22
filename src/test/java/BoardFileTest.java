import org.testng.annotations.*;
import colman66.kakuro.server.KakuroSolver;
import com.fasterxml.jackson.core.*;
import com.fasterxml.jackson.databind.*;
import java.io.IOException;
import java.io.File;
import java.net.URL;
import java.net.URISyntaxException;
import static org.testng.Assert.*;
import java.nio.file.Path;
import com.fasterxml.jackson.databind.node.ArrayNode;
import org.testng.ITest;

public final class BoardFileTest implements ITest
{
    public String getTestName() {
        return basename;
    }

    private String basename;
    final ObjectMapper mapper = new ObjectMapper();

    private static File urlToFile(URL url) {
        try {
            return new File(url.toURI());
        } catch(URISyntaxException e) {
            return null;
        }
    }

    public BoardFileTest(String basename) {
        this.basename = basename;
    }

    @Test
    public void boardTest() throws JsonProcessingException, IOException {
        URL inputFileUrl = this.getClass().getResource(this.basename + ".json");
        JsonNode input = mapper.readTree(inputFileUrl);
        KakuroSolver solver = new KakuroSolver((ArrayNode) input);
        JsonNode output = solver.getSolvedJson();
        URL snapshotFileUrl = this.getClass().getResource(this.basename + ".output.json");
        if (snapshotFileUrl == null) {
            Path inputPath = urlToFile(inputFileUrl).toPath();
            Path buildPath = inputPath
                .getParent()
                .getParent()
                .getParent();
            Path testPath = buildPath
                .resolveSibling("src")
                .resolve("test");
            File outputFile = testPath
                .resolve("resources")
                .resolve(this.basename + ".output.json")
                .toFile();
            System.out.println(outputFile);
            outputFile.createNewFile();
            mapper.enable(SerializationFeature.INDENT_OUTPUT)
                .writeValue(outputFile, output);
        } else {
            assertEquals(output, mapper.readTree(snapshotFileUrl));
        }
    }
}