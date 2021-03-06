import org.apache.http.HttpEntity;
import org.apache.http.HttpHost;
import org.apache.http.HttpResponse;
import org.apache.http.auth.AuthScope;
import org.apache.http.client.AuthCache;
import org.apache.http.auth.UsernamePasswordCredentials;
import org.apache.http.client.CredentialsProvider;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.client.protocol.HttpClientContext;
import org.apache.http.impl.auth.BasicScheme;
import org.apache.http.impl.client.BasicAuthCache;
import org.apache.http.impl.client.BasicCredentialsProvider;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.impl.conn.DefaultProxyRoutePlanner;
import org.apache.http.util.EntityUtils;
import org.json.JSONArray;
import org.json.JSONObject;





//import java.util.Base64;
import java.util.Map;

import javax.xml.bind.DatatypeConverter;

/**
 * A sample Java Client that runs outside of Bluemix that accesses the REST
 * endpoint of a GraphDB Service instance running in Bluemix.
 *
 */
public class SampleBluemixGraphDbClient
{
    private CloseableHttpClient client = null;
    private String apiURL = null;
    private String userId = null;
    private String password = null;

    public static void main(String[] args)
    {
        SampleBluemixGraphDbClient me = new SampleBluemixGraphDbClient();
        me.doWork();
    }

    private void doWork()
    {
        initialize();
        createAVertex();
    }


    /**
     * It is bad practice to hard code the url/userid/password in a program like this.
     *
     * Better would be to store this information in a protected and/or encrypted file
     * and read the values in at runtime.  For clarify, and simplicity of the example code,
     * the values are simply hard coded here.
     *
     */
    private void initialize()
    {
        //client = HttpClients.createDefault();
        HttpHost proxy = new HttpHost("kuzh.polytechnique.fr", 8080, "http");
        DefaultProxyRoutePlanner routePlanner = new DefaultProxyRoutePlanner(proxy);
        client = HttpClients.custom().setRoutePlanner(routePlanner).build();
        
        // curl -u 93df7adc-5dd9-446c-83f5-8d6d18c3b3bb:320f5ee2-90c9-430b-a2b4-312b25a8e6f7 "https://graphrestify.stage1.ng.bluemix.net/graphs/a15ccb5d-ce94-45dd-8638-02c82295bad7/g61089256"

        // replace the url shown here with the URL specfic to your graph instance from your JSON - labeled api URL
        apiURL = "https://graphrestify-alpha.eu-gb.bluemix.net/dd7d5436-241e-48d6-8989-1551fdb5ee92/g";
        // replace the user id shown here with the user id provided for your graph instance
        userId = "368949f6-fb00-4a67-92cd-d0a80252f6cb";
        // replace the password shown here with the password provided for your graph instance
        password = "6d2a4068-c353-4e50-8d50-54397b9ae539";
    }


    /**
     *
     */
    private void createAVertex()
    {
        try
        {
            String postURL = apiURL + "/vertices";

            // POST our new vertex request to the bluemix service
            HttpPost httpPost = new HttpPost(postURL);
            byte[] userpass = (userId + ":" + password).getBytes();
            byte[] encoding = DatatypeConverter.printBase64Binary(userpass).getBytes();
            httpPost.setHeader("Authorization", "Basic " + new String(encoding));

            // send the post and retrieve the response from the Bluemix service
            HttpResponse httpResponse = client.execute(httpPost);
            HttpEntity httpEntity = httpResponse.getEntity();
            String content = EntityUtils.toString(httpEntity);
            EntityUtils.consume(httpEntity);

            // the JSON response body from the Bluemix GraphDB service
            JSONObject jsonContent = new JSONObject(content);
            System.out.println(content);

            // TODO: check for a 401 - Not Authorized Message
            JSONObject result = jsonContent.getJSONObject("result");
            JSONArray data = result.getJSONArray("data");
            if (data.length() > 0)
            {
                JSONObject newVertex = data.getJSONObject(0);
                System.out.println(newVertex);
            }
        }
        catch (Exception e)
        {
           e.printStackTrace();
        }


    }

}
