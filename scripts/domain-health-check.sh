#!/bin/bash
# Hardcard Domain Health Check
# Monitors DNS propagation and SSL certificate status for all Hardcard domains

set -e

BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BOLD}${CYAN}"
echo "🏛️  HARDCARD DOMAIN HEALTH CHECK"
echo "================================${NC}"
echo ""

# Function to check DNS record
check_dns() {
    local domain=$1
    local record_type=$2
    local expected=$3

    echo -e "${BOLD}Checking $domain ($record_type)...${NC}"

    result=$(dig +short "$domain" "$record_type" 2>/dev/null || echo "ERROR")

    if [[ "$result" == "ERROR" ]] || [[ -z "$result" ]]; then
        echo -e "  ${RED}✗ No $record_type record found${NC}"
        return 1
    elif [[ "$expected" != "" ]] && [[ "$result" == *"$expected"* ]]; then
        echo -e "  ${GREEN}✓ $record_type: $result${NC}"
        return 0
    else
        echo -e "  ${YELLOW}⚠ $record_type: $result${NC}"
        if [[ "$expected" != "" ]]; then
            echo -e "    ${YELLOW}Expected: $expected${NC}"
        fi
        return 2
    fi
}

# Function to check HTTPS/SSL
check_https() {
    local url=$1

    echo -e "${BOLD}Checking HTTPS: $url${NC}"

    # Check if site responds
    http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$url" 2>/dev/null || echo "000")

    if [[ "$http_code" == "200" ]]; then
        echo -e "  ${GREEN}✓ HTTP 200 OK${NC}"

        # Check SSL certificate
        ssl_info=$(curl -vI "$url" 2>&1 | grep -E "SSL certificate verify|subject:|issuer:" | head -3)
        if [[ "$ssl_info" == *"OK"* ]] || [[ "$ssl_info" == *"Let's Encrypt"* ]]; then
            echo -e "  ${GREEN}✓ SSL Certificate Valid${NC}"
        else
            echo -e "  ${YELLOW}⚠ SSL Status unclear${NC}"
        fi
    elif [[ "$http_code" == "404" ]]; then
        echo -e "  ${YELLOW}⚠ HTTP 404 Not Found (DNS works, but no content)${NC}"
    elif [[ "$http_code" == "000" ]]; then
        echo -e "  ${RED}✗ Connection failed (DNS not propagated or site down)${NC}"
    else
        echo -e "  ${YELLOW}⚠ HTTP $http_code${NC}"
    fi
}

# Function to check page title
check_content() {
    local url=$1
    local expected_title=$2

    echo -e "${BOLD}Checking content at $url${NC}"

    title=$(curl -s "$url" 2>/dev/null | grep -o '<title>.*</title>' | sed 's/<title>\(.*\)<\/title>/\1/' || echo "")

    if [[ -z "$title" ]]; then
        echo -e "  ${RED}✗ No content retrieved${NC}"
    elif [[ "$title" == *"$expected_title"* ]]; then
        echo -e "  ${GREEN}✓ Title: $title${NC}"
    else
        echo -e "  ${YELLOW}⚠ Title: $title${NC}"
        if [[ "$expected_title" != "" ]]; then
            echo -e "    ${YELLOW}Expected: *$expected_title*${NC}"
        fi
    fi
}

echo ""
echo -e "${BOLD}${CYAN}═══════════════════════════════════════${NC}"
echo -e "${BOLD}${CYAN}CHECKING: hardcard.world (Economic Hub)${NC}"
echo -e "${BOLD}${CYAN}═══════════════════════════════════════${NC}"
echo ""

check_dns "hardcard.world" "A" "199.36.158.100"
check_dns "hardcard.world" "CNAME" "hardcard-world-prod.web.app"
check_https "https://hardcard.world"
check_content "https://hardcard.world" "Hardcard World"

echo ""
echo -e "${BOLD}${CYAN}═══════════════════════════════════════${NC}"
echo -e "${BOLD}${CYAN}CHECKING: hardcard.org (The Cathedral)${NC}"
echo -e "${BOLD}${CYAN}═══════════════════════════════════════${NC}"
echo ""

check_dns "hardcard.org" "A" ""
check_dns "hardcard.org" "CNAME" ""
check_https "https://hardcard.org"
check_content "https://hardcard.org" "Cathedral"

echo ""
echo -e "${BOLD}${CYAN}═══════════════════════════════════════${NC}"
echo -e "${BOLD}${CYAN}CHECKING: Firebase Direct URLs${NC}"
echo -e "${BOLD}${CYAN}═══════════════════════════════════════${NC}"
echo ""

check_https "https://hardcard-world-prod.web.app"
check_content "https://hardcard-world-prod.web.app" "Hardcard World"

check_https "https://hardcard.web.app"
check_content "https://hardcard.web.app" ""

echo ""
echo -e "${BOLD}${CYAN}═══════════════════════════════════════${NC}"
echo -e "${BOLD}${CYAN}CHECKING: Premium Domains${NC}"
echo -e "${BOLD}${CYAN}═══════════════════════════════════════${NC}"
echo ""

for domain in "hardcard.ai" "hardcard.app" "hardcard.me" "hardcard.cc"; do
    echo -e "${BOLD}$domain:${NC}"
    check_dns "$domain" "A" ""
    check_dns "$domain" "CNAME" ""
    echo ""
done

echo ""
echo -e "${BOLD}${CYAN}═══════════════════════════════════════${NC}"
echo -e "${BOLD}${GREEN}HEALTH CHECK COMPLETE${NC}"
echo -e "${BOLD}${CYAN}═══════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}⏰ DNS Propagation typically takes:${NC}"
echo -e "   - Initial: 5-10 minutes"
echo -e "   - Full global propagation: 1-2 hours"
echo -e "   - Maximum (rare): 24-48 hours"
echo ""

echo -e "${CYAN}📊 Next Steps:${NC}"
echo -e "   1. Add DNS records in your domain registrar"
echo -e "   2. Run this script every 10 minutes to monitor:"
echo -e "      ${BOLD}watch -n 600 ./scripts/domain-health-check.sh${NC}"
echo -e "   3. When all checks are ${GREEN}green${NC}, you're LIVE! 🚀"
echo ""
