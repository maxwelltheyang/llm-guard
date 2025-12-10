import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.security.Key;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.util.Base64;
import org.jasypt.util.password.PasswordEncryptor;
import org.jasypt.util.password.PooledDigestPasswordEncryptor;

public class Main {

    private static final String CIPHER_SUITE = "AES/GCM/NoPadding";
    private static final int TAG_SIZE = 128;
    private static final int DEFAULT_ITERATION_COUNT = 2097152; // Increased iteration count for improved security
    private static final int SALT_SIZE = 32;

    public static void main(String[] args) {
        String configFilePath = System.getenv("config.file.path");
        if (configFilePath != null && !configFilePath.isEmpty()) {
            loadConfig(configFilePath);
        } else {
            // Use default or hardcoded configuration values
            String configFileContent = "key=secret-key\nsalt=generated-salt";
            storeConfig(configFileContent, "default-config.txt");
        }

        String username = "valid_username";
        String password = "password123";
        byte[] salt = generateSalt(username);
        Key key = deriveKey(password.getBytes(), salt);

        // Secure way to get the client's IP address (e.g., using X-Forwarded-For header in HTTP requests)
        String clientIP = getClientIP();

        String additionalAuthenticationFactor = configureAdditionalAuthenticationFactor(username, clientIP);
        if (additionalAuthenticationFactor != null && !additionalAuthenticationFactor.isEmpty()) {
            System.out.println("Additional Authentication Factor: " + additionalAuthenticationFactor);
        }

        String encryptedMessage = encryptMessage(key, salt, "message-to-encrypt");
        byte[] decryptedData = decryptMessage(key, encryptedMessage);
        System.out.println("Decrypted Data: " + new String(decryptedData));
    }

    private static void loadConfig(String configFilePath) {
        try {
            Properties props = new Properties();
            props.load(new FileInputStream(configFilePath));
            // Load configuration values from the properties file securely (e.g., using a secrets management system)
            String key = props.getProperty("key");
            String salt = props.getProperty("salt");
            System.out.println("Loaded config: " + key + ", " + salt);
        } catch (Exception e) {
            System.out.println("Error loading configuration: " + e.getMessage());
        }
    }

    private static void storeConfig(String configFileContent, String filename) {
        try (PrintWriter writer = new PrintWriter(filename)) {
            writer.println(configFileContent);
            System.out.println("Stored config in file: " + filename);
        } catch (Exception e) {
            System.out.println("Error storing configuration: " + e.getMessage());
        }
    }

    private static byte[] generateSalt(String username) {
        SecureRandom random = new SecureRandom();
        byte[] salt = new byte[SALT_SIZE];
        random.nextBytes(salt);
        return salt;
    }

    private static Key deriveKey(byte[] password, byte[] salt) {
        PooledDigestPasswordEncryptor encryptor = new PooledDigestPasswordEncryptor(256, DEFAULT_ITERATION_COUNT);
        byte[] derivedKey = encryptor.derive(password, salt);
        return new SecretKeySpec(derivedKey, "AES");
    }

    private static String configureAdditionalAuthenticationFactor(String username, String clientIP) {
        // Use a secure authentication mechanism (e.g., digital signatures)
        return username + "|" + clientIP;
    }

    private static String getClientIP() {
        // Use a secure way to get the client's IP address
        return "192.168.1.100";
    }

    private static String encryptMessage(Key key, byte[] salt, String message) throws Exception {
        Cipher cipher = Cipher.getInstance(CIPHER_SUITE);
        GCMParameterSpec spec = new GCMParameterSpec(TAG_SIZE, salt);
        cipher.init(Cipher.ENCRYPT_MODE, key, spec);
        byte[] encryptedData = cipher.doFinal(message.getBytes());
        return Base64.getEncoder().encodeToString(encryptedData) + "|" + Base64.getEncoder().encodeToString(spec.getIV());
    }

    private static byte[] decryptMessage(String encryptedMessage) throws Exception {
        String[] parts = encryptedMessage.split("|");
        byte[] encryptedData = Base64.getDecoder().decode(parts[0]);
        byte[] iv = Base64.getDecoder().decode(parts[1]);
        Cipher cipher = Cipher.getInstance(CIPHER_SUITE);
        GCMParameterSpec spec = new GCMParameterSpec(TAG_SIZE, iv);
        cipher.init(Cipher.DECRYPT_MODE, new SecretKeySpec(new byte[]{}, "AES"), spec);
        return cipher.doFinal(encryptedData);
    }
}
